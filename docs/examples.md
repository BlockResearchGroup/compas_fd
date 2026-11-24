# Worked examples

## Loaded network

This example follows the linear equilibrium equations in
[Schek (1974)](https://doi.org/10.1016/0045-7825(74)90045-0). The anchors sit at
`(0, 0, 0)` and `(4, 0, 0)`, with force densities 1 and 3. A downward load
of 4 puts the free vertex at `(3, 0, -1)`.

```python
--8<-- "docs/examples/loaded_network.py"
```

## Viewer examples

### Mesh with fixed corners or an arch

Run the scripts from the repository root in the interactive COMPAS 3
environment with this package and `compas_viewer` installed. The arch example
also requires `compas_occ` and its native `pythonocc-core` dependency.

```sh
python docs/examples/viewer/mesh_fixed_corners.py
python docs/examples/viewer/mesh_on_arch.py
```

Both grids have fixed corners (red) and higher force density along the
boundary. In the second example, the middle row slides along a NURBS arch
(blue). Green lines show support reactions, scaled for display.

```python
--8<-- "docs/examples/viewer/mesh_fixed_corners.py"
```

```python
--8<-- "docs/examples/viewer/mesh_on_arch.py"
```

## Historical illustrations

A mesh with fixed corners can also have a row of sliding supports on a NURBS
arch. The image shows the configuration from an earlier COMPAS 2 viewer run.

![Mesh supported by an arch](assets/images/example_mesh_constrained_on-arch.png)
