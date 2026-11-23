from collections.abc import Callable
from collections.abc import Sequence
from typing import Any
from typing import cast

import numpy as np
from compas.linalg import normrow

from compas_fd._scipy import dot_coordinates
from compas_fd._scipy import row_lengths
from compas_fd._scipy import solve_coordinates
from compas_fd.constraints import Constraint
from compas_fd.types import FloatArray
from compas_fd.types import FloatNx3

from .fd_numerical_data import FDNumericalData
from .result import Result


def fd_constrained_numpy(
    *,
    vertices: FloatNx3,
    fixed: list[int],
    edges: Sequence[tuple[int, int]],
    forcedensities: Sequence[float],
    loads: FloatNx3 | None = None,
    constraints: Sequence[Constraint[Any] | None],
    kmax: int = 100,
    tol_res: float = 1e-3,
    tol_disp: float = 1e-3,
    damping: float = 0.1,
    selfweight: Callable[[FloatArray], FloatArray] | None = None,
) -> Result:
    """Iteratively solve for equilibrium with geometric vertex constraints.

    Parameters
    ----------
    vertices : FloatNx3
        Initial XYZ coordinates in vertex-index order, shape `(n, 3)`.
    fixed : list[int]
        Indices of fixed vertices.
    edges : list[tuple[int, int]]
        Edges as pairs of vertex indices.
    forcedensities : list[float]
        Axial force per unit length for each edge, in edge order.
    loads : FloatNx3, optional
        Applied force vectors, shape `(n, 3)`. Defaults to zero.
    constraints : sequence of Constraint or None
        One entry per vertex. Use `None` for vertices without a constraint.
        Place vertices that may slide along a constraint in `fixed` so the
        sparse solve holds them while the constraint update moves them.
    kmax : int, optional
        Maximum number of iterations.
    tol_res : float, optional
        Tolerance for the maximum tangential residual at constrained vertices.
    tol_disp : float, optional
        Displacement tolerance in coordinate units. The current implementation
        updates the coordinate array in place, so the displacement check
        compares the same array across iterations.
    damping : float, optional
        Damping factor for the geometry update of constrained vertices between two iterations.
    selfweight : callable, optional
        Function that takes the current `(n, 3)` coordinates and returns an
        `(n, 1)` array of weights subtracted from the Z loads.

    Returns
    -------
    Result
        Coordinates after the last constraint update. Residuals are computed
        from the supplied loads and the coordinates before that update.

    See Also
    --------
    fd_numpy

    Notes
    -----
    The solver updates the supplied constraint objects. A compatible float64
    input coordinate array may also be updated in place.

    """
    numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    for _ in range(kmax):
        xyz_prev = numdata.xyz
        _solve_fd(numdata, selfweight)
        # this needs to be turned inside out
        # - associate vertices with constraint
        # - compute all projections in one step
        # - vectorize the computation of residuals
        # -
        _update_constraints(numdata, constraints, damping)
        if _is_converged_residuals(numdata.tangent_residuals, tol_res) and _is_converged_disp(xyz_prev, numdata.xyz, tol_disp):
            break

    _post_process_fd(numdata)
    return numdata.to_result()


def _solve_fd(numdata: FDNumericalData, selfweight: Callable[[FloatArray], FloatArray] | None = None) -> None:
    """
    Solve a single iteration for the equilibrium coordinates of a system.
    All updated numerical arrays are stored in the numdata parameter.
    """
    p = numdata.p.copy()
    if selfweight:
        p[:, 2] -= selfweight(numdata.xyz)[:, 0]

    p = p[numdata.free]
    b = p - dot_coordinates(numdata.Af, numdata.xyz[numdata.fixed])
    numdata.xyz[numdata.free] = solve_coordinates(numdata.Ai, b)
    numdata.residuals = numdata.p - dot_coordinates(numdata.A, numdata.xyz)


def _post_process_fd(numdata: FDNumericalData) -> None:
    """
    Compute dependent numerical arrays from the numerical data after running solver.
    All updated numerical arrays are stored in the numdata parameter.
    """
    lengths = normrow(dot_coordinates(numdata.C, numdata.xyz))
    numdata.lengths = lengths
    numdata.forces = numdata.q * lengths


def _update_constraints(numdata: FDNumericalData, constraints: Sequence[Constraint[Any] | None], damping: float) -> None:
    """
    Update all vertex constraints by the residuals of the current iteration,
    and store their updated vertex coordinates in the numdata parameter.
    """
    # The solver populates residuals before updating constraints.
    residuals = cast(FloatArray, numdata.residuals)
    for vertex, constraint in enumerate(constraints):
        if not constraint:
            continue
        constraint.location = numdata.xyz[vertex]
        constraint.residual = residuals[vertex]
        constraint.update(damping=damping)
        numdata.xyz[vertex] = cast("Sequence[float]", constraint.location)
    numdata.tangent_residuals = np.asarray([c.tangent for c in constraints if c])


def _is_converged_residuals(residuals: FloatArray | None, tol_res: float) -> bool:
    """
    Verify whether the maximum constraint residual is within tolerance.
    """
    if residuals is None or not residuals.any():
        return True
    max_res = max(row_lengths(residuals))
    return max_res < tol_res


def _is_converged_disp(
    old_xyz: FloatArray,
    new_xyz: FloatArray,
    tol_disp: float,
) -> bool:
    """
    Verify whether the maximum coordinate displacement
    between consecutive iterations is within tolerance.
    """
    max_dxyz = max(row_lengths(new_xyz - old_xyz))
    return max_dxyz < tol_disp
