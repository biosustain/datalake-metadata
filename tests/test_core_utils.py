import json
import unittest
from unittest.mock import patch

import datalake_metadata
from jsonschema import Draft202012Validator
from semantic_version import SimpleSpec, Version


class TestCoreUtils(unittest.TestCase):
    version = SimpleSpec(">=0.0.1-alpha")

    @staticmethod
    def get_metadata():
        # defined as function call to always return a new copy (to avoid side effects)
        return {
            "$schema": Draft202012Validator.META_SCHEMA["$id"],
            "version": "0.0.1-alpha",
            "Dataset": {
                "CKAN_dataset_metadata": {
                    "dataset_id": "example_dataset_id",
                    "data_type": "example_data_type",
                    "instrument": "example_instrument",
                },
                "Benchling_Experiment_metadata": {
                    "experiment_id": "example_experiment_id",
                    "experiment_type": "example_experiment_type",
                },
                "Benchling_Request_metadata": {
                    "request_id": "example_request_id",
                    "schema": "example_schema",
                },
            },
            "Sample_Sheet": {"path": "nanopore_sample_submission_sample_sheet_path"},
            "CKAN_Resources": [
                {"resource_name": "example_resource_name_1", "path": "example_path_1"},
                {"resource_name": "example_resource_name_2", "path": "example_path_2"},
            ],
        }

    def test_load(self):
        import io

        in_mem_file = io.StringIO(json.dumps(self.get_metadata()))

        datalake_metadata.load(in_mem_file, self.version)

    def test_loads(self):
        datalake_metadata.loads(json.dumps(self.get_metadata()), self.version)

    @patch.object(datalake_metadata, "validate_metadata")
    @patch.object(datalake_metadata, "migrations", new_callable=dict)
    def test_migration(self, migrations, validate_mock):
        migrations[SimpleSpec("<0.1.0")] = lambda instance: instance.update(
            {"version": "0.1.0"}
        )
        metadata = self.get_metadata()
        datalake_metadata.migrate_metadata(metadata, "=0.1.0")
        self.assertEqual(metadata["version"], "0.1.0")
        validate_mock.assert_called()

    def test_migration_not_implemented(self):
        metadata = self.get_metadata()
        with self.assertRaises(ValueError):
            datalake_metadata.migrate_metadata(metadata, "=0.2.0")

    @patch.object(datalake_metadata, "validate_metadata")
    @patch.object(datalake_metadata, "migrations", new_callable=dict)
    def test_migration_overshoot(self, migrations, validate_mock):
        migrations[SimpleSpec("<0.1.0")] = lambda instance: instance.update(
            {"version": "0.1.0"}
        )
        mock_0_2_0_migration = unittest.mock.MagicMock()
        migrations[SimpleSpec("<0.2.0")] = mock_0_2_0_migration
        metadata = self.get_metadata()
        datalake_metadata.migrate_metadata(metadata, "=0.1.0")
        self.assertEqual(metadata["version"], "0.1.0")
        mock_0_2_0_migration.assert_not_called()
        validate_mock.assert_called()

    @patch.object(datalake_metadata, "validate_metadata")
    @patch.object(datalake_metadata, "update_version")
    def check_migrations_updates_version(
        self, update_version, validate_mock, migrations
    ):
        metadata = self.get_metadata()
        for migration in migrations.values():
            validate_mock.reset_mock()
            update_version.reset_mock()
            init_version = Version(metadata["version"])
            migration(metadata)
            self.assertNotEqual(
                # compare versions truncated to patch level
                # each migration should update at least patch level
                init_version.truncate(),
                Version(metadata["version"]).truncate(),
            )
            # Utility function to update version should be called in each migration
            update_version.assert_called_once()
            # Metadata should be validated after each migration
            validate_mock.assert_called_once()

    @patch.object(datalake_metadata, "library_version", Version("0.0.3-dev7+gabcdef"))
    def test_update_version_add_lib_prerelease_and_build(self):
        init_version = "0.0.1"
        instance = dict(version=init_version)
        updated_version = datalake_metadata.update_version(instance, Version("0.0.2"))
        self.assertEqual(
            str(updated_version),
            instance["version"],
            "Version should be updated in place",
        )
        self.assertEqual(
            tuple(["dev7"]),
            updated_version.prerelease,
            "Prerelease should be updated to library version",
        )
        self.assertEqual(
            tuple(["gabcdef"]),
            updated_version.build,
            "Build should be updated to library version",
        )
