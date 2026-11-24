# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added analytical equilibrium, constraint and installed-plugin regression tests.
* Added COMPAS 3 Viewer examples for fixed and arch-supported meshes.

### Changed

* Aligned numerical imports, plugin discovery and constraint serialization with COMPAS 3.
* Updated the supported Python versions to 3.12–3.14 and added locked development tools.
* Migrated the documentation build to MkDocs and updated solver annotations and docstrings.
* Organised the documentation assets, archived COMPAS 2 viewer scripts, and added the maintained example to the Pyright check.
* Organised the maintained examples into named sections and formatted longer calls with one argument per line.
* Simplified the loaded-network example to demonstrate solver inputs and results.

### Removed

* Removed the legacy `DATASCHEMA` attributes from all constraints to align with COMPAS 3. Existing constraint JSON payloads remain supported.
* Removed the superseded reStructuredText pages and Sphinx configuration.
* Removed the legacy Viewer examples and the `scripts/` and `notebooks/` folders.
* Removed the unused `temp/` placeholder directory.

## [0.5.4] 2024-11-10

### Added

* Added `compas` back to requirements.

### Changed

### Removed


## [0.5.3] 2024-11-10

### Added

### Changed

### Removed

* Removed `compas` from requirements to solve problem in Rhino plugins.


## [0.5.2] 2024-10-23

### Added

* Added `compas_fd.types.IntNx2`.

### Changed

### Removed


## [0.5.1] 2024-05-14

### Added

### Changed

### Removed


## [0.5.0] 2024-02-29

### Added

### Changed

* Updated `build` and `docs` workflows to `v4`
* Remove dependency on `nptyping` and `typing_extensions`.
* Switch to `pyproject.toml`.

### Removed


## [0.4.2] 2024-02-09

### Added

### Changed

* Updated workflows.

### Removed


## [0.4.1] 2022-09-22

### Added

### Changed

### Removed


## [0.4.0] 2022-09-21

### Added

### Changed

* Fixed workflow errors.

### Removed


## [0.3.1] 2022-03-23

### Added

### Changed

### Removed


## [0.3.0] 2022-03-22

### Added

* Workflow for changelog check.
* Support for python 3.10

### Changed

* Update build workflow version

### Removed

* Release candidate option.
