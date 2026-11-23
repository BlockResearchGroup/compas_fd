# Solvers and loads

The force density of an edge is its axial force divided by its length. With
prescribed densities and fixed supports, the free-vertex equilibrium equations
are linear. See [Schek (1974)](https://doi.org/10.1016/0045-7825(74)90045-0) for
the derivation.

Provide XYZ coordinates and loads in vertex-index order, with one row per
vertex. Provide one force density per edge. Use consistent length and force
units. The direct solver, `fd_numpy`, returns equilibrated coordinates and
residuals in vertex order, and axial forces and lengths in edge order.

Use `fd_constrained_numpy` when supports can move along a line, plane, curve
or surface. The `constraints` sequence has one entry per vertex, with `None`
for vertices without a constraint. Pass the indices of movable supports in
`fixed` so their coordinates are held during the sparse solve and changed by
the constraint update. NURBS operations need a compatible COMPAS geometry
backend.

`SelfweightCalculator` takes a COMPAS mesh with a vertex thickness attribute.
Given current vertex coordinates in mesh order, it returns one positive
weight per vertex. Pass the calculator as `selfweight` to the constrained
solver to subtract these weights from the applied Z loads.
