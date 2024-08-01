import json
import unittest
from unittest.mock import patch

import datalake_metadata
from jsonschema import Draft202012Validator
from semantic_version import SimpleSpec


class Testv0_0_1(unittest.TestCase):
    version = SimpleSpec(">=0.0.1-alpha")

    def get_metadata(self):
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

    def test_migration_not_implemented(self):
        metadata = self.get_metadata()
        with self.assertRaises(ValueError):
            datalake_metadata.migrate_metadata(metadata, "=0.2.0")
