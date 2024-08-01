# (Biosustain's) datalake-metadata
This repository contains python package for managing metadata in the biosustain datalake.

## Motivation
Increasing number of applications in the biosustain datalake require metadata to be stored and managed.
This package provides unified way to load, validate and manage metadata in the datalake.

## Installation
```bash
pip install git+https://github.com/biosustain/datalake-metadata.git
```

## Semantic versioning
This project follows the [semantic versioning](https://semver.org/) scheme to denote the compatibility of the schema as well as the package.
Schema version is denoted with the format "major.minor.patch". While package version can be meantioned in 'pre-release' or 'build metadata' format.


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
