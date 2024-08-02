# (Biosustain's) datalake-metadata
This repository contains python package for managing metadata in the biosustain datalake.

## Motivation
Increasing number of applications in the biosustain datalake require metadata to be stored and managed.
This package provides unified way to load, validate and manage metadata in the datalake.

## Installation
For lastest release:
```bash
pip install git+https://github.com/biosustain/datalake-metadata.git
```
For specific release:
```bash
pip install git+https://github.com/biosustain/datalake-metadata.git@{tag}
```

## Semantic versioning
This project follows the [semantic versioning](https://semver.org/) scheme to denote the compatibility of the schema as well as the package.
Schema version is denoted with the format "major.minor.patch". While package version can be meantioned in 'pre-release' or 'build'.

### Library versioning
The library version is updated according to the following rules:

- Major, minor, and patch should reflect newest schema version.
- Pre-release is in format "devN" where N is the number of commits since the last release.
- Build is in format "g{short commit hash}".

For more details please refer to [hatch-vcs](https://github.com/ofek/hatch-vcs) and [setuptools-scm](https://setuptools-scm.readthedocs.io/en/latest/usage/#default-versioning-scheme) documentation.

## Usage
### Loading metadata
"loads" method is used to load metadata.
Resulted metadata adheres to the schema version specified in the second argument.
```python
import datalake_metadata

with open('metadata.json', 'r') as f:
    metadata = datalake_metadata.load(f, '0.0.*')
```

### Validating metadata
"validate" method is used to validate metadata. It raises an exception if the metadata is invalid.
```python
import datalake_metadata

metadata = {}

datalake_metadata.validate_metadata(metadata)
```

## Code style guide
This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
It is intended that all schema definitions merged to the master branch becomes immutable.
