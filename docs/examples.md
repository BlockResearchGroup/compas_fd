# Worked examples

## Loaded network

This example follows the linear equilibrium equations in
[Schek (1974)](https://doi.org/10.1016/0045-7825(74)90045-0). The anchors sit at
`(0, 0, 0)` and `(4, 0, 0)`, with force densities 1 and 3. A downward load
of 4 puts the free vertex at `(3, 0, -1)`.

```python
--8<-- "docs/examples/loaded_network.py"
```

## Arch support illustration

A mesh with fixed corners can also have a row of sliding supports on a NURBS
arch. The image shows the configuration from an earlier COMPAS 2 viewer run.

![Mesh supported by an arch](assets/images/example_mesh_constrained_on-arch.png)
