# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added numerical baselines recorded with COMPAS 2 (`tests/baselines`) and tests that compare the results of `fd_numpy`, `fd_constrained_numpy`, and `SelfweightCalculator` against them.
* Added tests for the import of every public module, for constraint dispatch and data, and closed-form tests for `CircleConstraint` and `SurfaceConstraint`.

### Changed

* Ported to COMPAS 3: `compas_fd` now requires `compas >=3.0.0,<4` and Python 3.12 or later. COMPAS 2 is no longer supported.
* Changed the imports of `connectivity_matrix` and `face_matrix` to `compas.linalg` (was `compas.matrices`), and of `cross_vectors`, `length_vector`, and `vector_component` to `compas.linalg` (was `compas.geometry`). Results are unchanged with respect to COMPAS 2.
* Changed `SurfaceConstraint.compute_normal` to use `NurbsSurface.normal_at`; `Surface.curvature_at` does not exist in COMPAS 3.
* `CircleConstraint` now works on a `compas.geometry.Circle`, because COMPAS 3 implements `Circle.closest_point(return_parameter=True)`.

### Removed

* Removed the `DATASCHEMA` class attributes of the constraints; COMPAS 3 has no data schemas.
* Removed `compas_fd.install` and `compas_fd.__all_plugins__` (the Rhino installer plugin); COMPAS 3 has no `compas_rhino` and discovers plugins through entry points only.
* Removed the `from __future__` imports and other Python 2 residue.

### Not verified against COMPAS 2

* `CurveConstraint` and `SurfaceConstraint` need a NURBS backend such as `compas_occ`, which is not a requirement of `compas_fd`. `CurveConstraint` is verified against a COMPAS 2 baseline with `compas_occ`.
* `SurfaceConstraint` and `CircleConstraint` on a `Circle` did not work with COMPAS 2 and have no baseline; they are verified against closed-form values with COMPAS 3 only.
* Loading a `CircleConstraint` from data (for example with `compas.json_loads`) fails, as it did before the port.
* Python 3.13 and 3.14 are declared but have not been tested yet.


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
