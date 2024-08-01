import json
from pathlib import Path
from string import Template
from typing import Any, Dict, Protocol, TypeAlias, TypeVar, Union, runtime_checkable

from jsonschema import validate
from semantic_version import SimpleSpec, Version
from semantic_version.base import BaseSpec
from .version import __version__

SCHEMA_PATH_TEMPLATE = Template("schemas/metadata-v${version}.schema.json")

Metadata: TypeAlias = Dict[str, Any]


def validate_metadata(instance):
    version = Version(instance["version"])
    schema_path = Path(__file__).parent / SCHEMA_PATH_TEMPLATE.substitute(
        version=version.truncate()
    )
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
        validate(instance=instance, schema=schema)


class Migration(Protocol):
    def __call__(self, instance: Metadata) -> None:
        """
        Migrate the metadata to the new schema

        NOTE: This function modifies the instance in place.

        Example:
        ```
        def migrate_to_0_1_0(instance):
            instance.update({
                "version": "0.1.0"
            })
        ```

        :param instance: metadata instance
        :return: None
        """


migrations: Dict[BaseSpec, Migration] = {}

VersionSpec: TypeAlias = Union[BaseSpec, str]


def migrate_metadata(instance, target_version_spec: VersionSpec):
    """
    Migrate the metadata to the target version.
    NOTE: This function modifies the instance in place.
    NOTE2: Returned instance is already validated.
    :param instance: metadata instance
    :param target_version_spec: target version (example: "=0.0.*")
    :return:
    """
    if isinstance(target_version_spec, str):
        target_version_spec = SimpleSpec(target_version_spec)

    current_version = Version(instance["version"])
    if not target_version_spec.match(current_version):
        for spec, migration in migrations.items():
            if spec.match(current_version):
                migration(instance)
                validate_metadata(instance)

        migrated_version = Version(instance["version"])

        if not target_version_spec.match(migrated_version):
            raise ValueError(f"Could not migrate metadata to {target_version_spec}")

    return instance


def loads(metadata: Union[str, Metadata], target_version_spec: VersionSpec) -> Metadata:
    """Load metadata from a string or a dictionary

    This function also migrates the metadata to the target version if necessary.
    Returned metadata is already validated.
    It is intended in place of `json.loads` function.

    NOTE: This function migrates/modifies the metadata in place.

    :param metadata: metadata as a json string or a dictionary
    :param target_version_spec: target version example: "=0.1.*"
    :return: metadata as a dictionary
    """
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    validate_metadata(metadata)
    migrate_metadata(metadata, target_version_spec)
    return metadata


# Extracted from stdlib typeshed
_T_co = TypeVar("_T_co", str, bytes)


@runtime_checkable
class SupportsRead(Protocol[_T_co]):
    def read(self, __length: int = ...) -> _T_co: ...


def load(metadata: SupportsRead, target_version_spec: VersionSpec) -> Metadata:
    """Load metadata from a file-like object

    This function also migrates the metadata to the target version if necessary.
    Returned metadata is already validated.
    It is intended in place of `json.load` function.

    :param metadata: file-like object containing json encoded metadata
    :param target_version_spec: target version example: "=0.1.*"
    :return: metadata as a dictionary
    """
    return loads(json.load(metadata), target_version_spec)


__all__ = [
    "Metadata",
    "VersionSpec",
    "validate_metadata",
    "migrate_metadata",
    "loads",
    "load",
    "__version__",
]
