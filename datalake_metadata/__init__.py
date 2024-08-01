import json
from pathlib import Path
from string import Template
from typing import Any, Dict, Protocol, TypeAlias, TypeVar, Union, runtime_checkable

from jsonschema import validate
from semantic_version import SimpleSpec, Version
from semantic_version.base import BaseSpec

from .version import version_tuple

library_version = Version(
    **dict(zip(["major", "minor", "patch"], version_tuple[:3])),
    **dict(zip(["prerelease", "build"], map(lambda p: [p], version_tuple[3:]))),
)

SCHEMA_PATH_TEMPLATE = Template("schemas/metadata-v${version}.schema.json")


def validate_metadata(instance):
    instance_version = Version(instance["version"])
    schema_path = Path(__file__).parent / SCHEMA_PATH_TEMPLATE.substitute(
        version=instance_version.truncate()
    )
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
        validate(instance=instance, schema=schema)


def update_version(instance, new_version: Version) -> Version:
    """
    Update the version of the metadata instance

    This helper method should be used in migration functions to update the version
     of the metadata instance, denoting the library build version.
    :param instance: metadata instance
    :param new_version: intended version
    :return: resolved version
    """
    complete_version = new_version.truncate()
    complete_version.prerelease = library_version.prerelease
    # if library has only tag version, use it as build version
    # (this is the case for stable releases)
    complete_version.build = library_version.build or str(library_version)
    instance.update({"version": str(complete_version)})
    return complete_version


class Migration(Protocol):
    def __call__(self, instance: Dict[str, Any]) -> None:
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
    for spec, migration in migrations.items():
        if target_version_spec.match(current_version):
            break
        if spec.match(current_version):
            migration(instance)
            validate_metadata(instance)
            current_version = Version(instance["version"])

    if not target_version_spec.match(current_version):
        raise ValueError(f"Could not migrate metadata to {target_version_spec}")

    return instance


def loads(metadata: Union[str, Dict[str, Any]], target_version_spec: VersionSpec) -> Dict[str, Any]:
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
    return migrate_metadata(metadata, target_version_spec)


# Extracted from stdlib typeshed
_T_co = TypeVar("_T_co", str, bytes, covariant=True)


@runtime_checkable
class SupportsRead(Protocol[_T_co]):
    def read(self, __length: int = ...) -> _T_co: ...


def load(metadata: SupportsRead, target_version_spec: VersionSpec) -> Dict[str, Any]:
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
    "VersionSpec",
    "validate_metadata",
    "migrate_metadata",
    "loads",
    "load",
]
