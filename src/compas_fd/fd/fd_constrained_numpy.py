from typing import Callable
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Literal
from typing_extensions import Annotated
from nptyping import NDArray
from nptyping import Float64

from numpy import asarray
from scipy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas.numerical import normrow

from compas_fd.constraints import Constraint
from compas_fd.fd.fd_numerical_data import FDNumericalData
from compas_fd.fd.result import Result


FloatNx3 = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Literal["*, 3"], Float64],
]


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
    """
    nd = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    for k in range(kmax):
        xyz_prev = nd.xyz
        _solve_fd(nd, selfweight)
        _update_constraints(nd, constraints, damping)
        if _is_converged_residuals(
            nd.tangent_residuals, tol_res
        ) and _is_converged_disp(xyz_prev, nd.xyz, tol_disp):
            break

    _post_process_fd(nd)
    return nd.to_result()


def _solve_fd(numdata: FDNumericalData, selfweight: Callable = None) -> None:
    """
    Solve a single iteration for the equilibrium coordinates of a system.
    All updated numerical arrays are stored in the numdata parameter.
    """
    nd = numdata

    p = nd.p.copy()
    if selfweight:
        p[:, 2] -= selfweight(nd.xyz)[:, 0]

    p = p[nd.free]
    b = p - nd.Af.dot(nd.xyz[nd.fixed])
    nd.xyz[nd.free] = spsolve(nd.Ai, b)
    numdata.residuals = nd.p - nd.A.dot(nd.xyz)


def _post_process_fd(numdata: FDNumericalData) -> None:
    """
    Compute dependent numerical arrays from the numerical data after running solver.
    All updated numerical arrays are stored in the numdata parameter.
    """
    nd = numdata
    nd.lengths = normrow(nd.C.dot(nd.xyz))
    numdata.forces = nd.q * nd.lengths


def _update_constraints(
    numdata: FDNumericalData, constraints: Sequence[Constraint], damping: float
) -> None:
    """
    Update all vertex constraints by the residuals of the current iteration,
    and store their updated vertex coordinates in the numdata parameter.
    """
    nd = numdata
    for vertex, constraint in enumerate(constraints):
        if not constraint:
            continue
        constraint.location = nd.xyz[vertex]
        constraint.residual = nd.residuals[vertex]
        constraint.update(damping=damping)
        nd.xyz[vertex] = constraint.location
    nd.tangent_residuals = asarray([c.tangent for c in constraints if c])


def _is_converged_residuals(
    residuals: NDArray[Literal["*, 3"], Float64], tol_res: float
) -> bool:
    """
    Verify whether the maximum constraint residual is within tolerance.
    """
    if residuals is None or not residuals.any():
        return True
    max_res = max(norm(residuals, axis=1))
    return max_res < tol_res


def _is_converged_disp(
    old_xyz: NDArray[Literal["*, 3"], Float64],
    new_xyz: NDArray[Literal["*, 3"], Float64],
    tol_disp: float,
) -> bool:
    """
    Verify whether the maximum coordinate displacement
    between consecutive iterations is within tolerance.
    """
    max_dxyz = max(norm(new_xyz - old_xyz, axis=1))
    return max_dxyz < tol_disp
