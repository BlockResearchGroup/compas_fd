from typing import Callable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

import numpy as np
from compas.linalg import normrow
from scipy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas_fd.constraints import Constraint
from compas_fd.types import FloatNx3

from .fd_numerical_data import FDNumericalData
from .result import Result


def fd_constrained_numpy(
    *,
    vertices: FloatNx3,
    fixed: List[int],
    edges: List[Tuple[int, int]],
    forcedensities: List[float],
    loads: Optional[FloatNx3] = None,
    constraints: Sequence[Constraint],
    kmax: int = 100,
    tol_res: float = 1e-3,
    tol_disp: float = 1e-3,
    damping: float = 0.1,
    selfweight=None,
) -> Result:
    """
    Iteratively compute the equilibrium coordinates of a system of vertices connected by edges.
    Vertex constraints are recomputed at each iteration.

    Parameters
    ----------
    vertices : FloatNx3
        Vertex coordinates.
    fixed : list[int]
        Indices of fixed vertices.
    edges : list[tuple[int, int]]
        Edges as pairs of vertex indices.
    forcedensities : list[float]
        Forcedensities of the edges.
    loads : FloatNx3, optional
        Loads on the vertices.
    constraints : list[:class:`~compas_fd.constraints.Constraint`]
        Vertex constraints.
    kmax : int, optional
        Maximum number of iterations.
    tol_res : float, optional
        Tolerance for the maximum residual force at the non-fixed vertices.
    tol_disp : float, optional
        Tolerance for the maximum displacement of the non-fixed vertices between two iterations.
    damping : float, optional
        Damping factor for the geometry update of constrained vertices between two iterations.
    selfweight : callable, optional
        Function that computes the selfweight of the vertices.

    Returns
    -------
    :class:`~compas_fd.solvers.result.Result`
        Result of the solver.

    See Also
    --------
    :func:`compas_fd.solvers.fd_numpy`

    Examples
    --------
    >>>

    """
    numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    for k in range(kmax):
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


def _solve_fd(numdata: FDNumericalData, selfweight: Callable = None) -> None:
    """
    Solve a single iteration for the equilibrium coordinates of a system.
    All updated numerical arrays are stored in the numdata parameter.
    """
    p = numdata.p.copy()
    if selfweight:
        p[:, 2] -= selfweight(numdata.xyz)[:, 0]

    p = p[numdata.free]
    b = p - numdata.Af.dot(numdata.xyz[numdata.fixed])
    numdata.xyz[numdata.free] = spsolve(numdata.Ai, b)
    numdata.residuals = numdata.p - numdata.A.dot(numdata.xyz)


def _post_process_fd(numdata: FDNumericalData) -> None:
    """
    Compute dependent numerical arrays from the numerical data after running solver.
    All updated numerical arrays are stored in the numdata parameter.
    """
    numdata.lengths = normrow(numdata.C.dot(numdata.xyz))
    numdata.forces = numdata.q * numdata.lengths


def _update_constraints(numdata: FDNumericalData, constraints: Sequence[Constraint], damping: float) -> None:
    """
    Update all vertex constraints by the residuals of the current iteration,
    and store their updated vertex coordinates in the numdata parameter.
    """
    for vertex, constraint in enumerate(constraints):
        if not constraint:
            continue
        constraint.location = numdata.xyz[vertex]
        constraint.residual = numdata.residuals[vertex]
        constraint.update(damping=damping)
        numdata.xyz[vertex] = constraint.location
    numdata.tangent_residuals = np.asarray([c.tangent for c in constraints if c])


def _is_converged_residuals(residuals: FloatNx3, tol_res: float) -> bool:
    """
    Verify whether the maximum constraint residual is within tolerance.
    """
    if residuals is None or not residuals.any():
        return True
    max_res = max(norm(residuals, axis=1))
    return max_res < tol_res


def _is_converged_disp(
    old_xyz: FloatNx3,
    new_xyz: FloatNx3,
    tol_disp: float,
) -> bool:
    """
    Verify whether the maximum coordinate displacement
    between consecutive iterations is within tolerance.
    """
    max_dxyz = max(norm(new_xyz - old_xyz, axis=1))
    return max_dxyz < tol_disp
