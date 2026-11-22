# Numerical baselines

Results of `compas_fd` on COMPAS 2, recorded before the COMPAS 3 port.
`tests/test_baselines.py` compares the current code against them.

**The recorded files are read-only.** `*.npz`, `constraints.json`, and
`provenance.json` are never regenerated or edited to make a test pass. A
deviation is a finding that needs a decision; the fixtures change only by
that decision. `record.py` refuses to write into a directory that already
holds a `provenance.json`.

## Files

| File | Content |
|---|---|
| `cases.py` | The single definition of the inputs and calls of every case. Uses only API that exists unchanged on COMPAS 2 and COMPAS 3. |
| `record.py` | Runs the cases under COMPAS 2 and writes the fixtures. |
| `fd-XX.npz` | One file per numerical case: inputs as `in_<name>`, outputs as `out_<name>`; `float64` or `int64`; loaded with `allow_pickle=False`. |
| `constraints.json` | fd-10: COMPAS 2 `json_dumps` of four constraints, one with `rhino_guid`. |
| `provenance.json` | Package commit, versions, platform, command, date, and the status of every case. |

## How they were produced

- Package: `compas_fd` at `7ee3c5a15bb304a71067638c758f1cad63995a91`,
  installed non-editable from Git (the commit is read from the
  `direct_url.json` of the installation).
- Environment: `brg-compas2` (`compas` 2.16.0, `compas_occ` 1.5.0 for
  fd-11); the exact versions are in `provenance.json`.
- Command, from the package root, on the commit that added this directory
  and before any change under `src/`:

  ```bash
  <brg-compas2 python> tests/baselines/record.py tests/baselines
  ```

`record.py` checks that `compas` is 2.x and that the imported `compas_fd` is
the installed legacy package, not the working tree.

## Cases

Shared input "grid": `Mesh.from_meshgrid(dx=10, nx=10)` (121 vertices, 220
edges), the four corners fixed, force density 10 on boundary edges and 1
inside, load (0, 0, -0.5) per vertex where stated. "Column" is the eleven
vertices at x = 5. In the constrained cases the column is also fixed, and
every column vertex has its own constraint object on its own copy of the
geometry. No random numbers.

| Case | Function | Input | Stored outputs |
|---|---|---|---|
| fd-01 | `fd_numpy` | grid, `loads=None` | vertices, residuals, forces, lengths |
| fd-02 | `fd_numpy` | grid, load | same |
| fd-03 | `SelfweightCalculator` | grid, t = 0.1, density 22, on the fd-02 geometry | dense `F`, selfweight |
| fd-04 | `fd_constrained_numpy` | grid, load, column on `Line([5, -1, 0], [5, 11, 0])`; `kmax=10`, `tol_res=0.0` | result arrays, constraint locations |
| fd-05 | `fd_constrained_numpy` | as fd-04 on `Plane([5, 0, 0], [1, 0, 0])` | same |
| fd-06 | `fd_constrained_numpy` | as fd-04 on `Vector(0, 1, 0)` | same |
| fd-07 | `fd_constrained_numpy` | as fd-04 on `Frame([5, 0, 0], [0, 1, 0], [0, 0, 1])` | same |
| fd-08 | `fd_constrained_numpy` with `selfweight` | fd-05 with a `SelfweightCalculator`, t = 0.1, density 1.0 | same |
| fd-09 | `fd_constrained_numpy`, early stop | fd-05 with `tol_res=0.1`, default `kmax` | same |
| fd-10 | constraint data | `json_dumps` of the Line, Plane, Vector, and Frame constraints; the Plane constraint has a `rhino_guid` | `constraints.json` |
| fd-11 | `fd_constrained_numpy` with a `CurveConstraint` | as fd-04 on `NurbsCurve.from_points([[5, 0, 0], [5, 5, 3], [5, 10, 0]])`; needs `compas_occ` | result arrays, constraint locations and parameters |

## Comparison

- Regenerated inputs equal the stored inputs exactly.
- Float outputs: `abs(new - base) <= 1e-9 + 1e-9 * abs(base)`.
- Integers and shapes: exact.
- fd-10: the stored JSON is loaded with `compas.json_loads` and the resulting
  constraints are compared with freshly built ones by type and `__data__`
  (the COMPAS guids in the text are random).
- `pytest tests/test_baselines.py -rP` prints the maximum absolute and
  relative deviation per output. In an environment that shares the numerical
  stack of the baseline the expected deviation is exactly 0; anything else
  is a finding even inside the tolerance.
- fd-11 is skipped when `compas_occ` is not installed.
