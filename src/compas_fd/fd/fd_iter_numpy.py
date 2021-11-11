from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from numpy import asarray
from numpy import float64
from scipy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas.numerical import normrow

from .fd_numerical_data import FDNumericalData
from .result import Result
from ..constraints import Constraint


def fd_iter_numpy(*,
                  vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
                  fixed: List[int],
                  edges: List[Tuple[int, int]],
                  forcedensities: List[float],
                  loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None,
                  constraints: Sequence[Constraint],
                  max_iter: int = 100,
                  tol_res: float = 1E-3,
                  tol_dxyz: float = 1E-3
                  ) -> Result:
    """Iteratively compute the equilibrium coordinates of a system of vertices connected by edges.
    Vertex constraints are recomputed at each iteration.
    """
    numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    for k in range(max_iter):
        xyz_prev = numdata.xyz
        _solve_fd(numdata)
        _update_constraints(numdata, constraints)
        if (_is_converged_residuals(numdata.tangent_residuals, tol_res) and
           _is_converged_xyz(xyz_prev, numdata.xyz, tol_dxyz)):
            break

    _post_process_fd(numdata)
    return numdata.to_result()


def _solve_fd(numdata: FDNumericalData) -> None:
    """Solve a single iteration for the equilibrium coordinates of a system.
    All updated numerical arrays are stored in the numdata parameter.
    """
    free, fixed, xyz, C, _, Q, p, Ai, Af, *_ = numdata
    b = p[free] - Af.dot(xyz[fixed])
    xyz[free] = spsolve(Ai, b)
    numdata.residuals = p - C.T.dot(Q).dot(C).dot(xyz)
    numdata.xyz = xyz


def _post_process_fd(numdata: FDNumericalData) -> None:
    """Compute dependent numerical arrays from the numerical data after running solver.
    All updated numerical arrays are stored in the numdata parameter.
    """
    _, _, xyz, C, q, *_ = numdata
    lengths = normrow(C.dot(xyz))
    numdata.forces = q * lengths
    numdata.lengths = lengths


def _update_constraints(numdata: FDNumericalData,
                        constraints: Sequence[Constraint]) -> None:
    """Update all vertex constraints by the residuals of the current iteration,
    and store their updated vertex coordinates in the numdata parameter.
    """
    xyz = numdata.xyz
    residuals = numdata.residuals
    for vertex, constraint in enumerate(constraints):
        if not constraint:
            continue
        constraint.location = xyz[vertex]
        constraint.residual = residuals[vertex]
        xyz[vertex] = constraint.location + constraint.tangent * 0.5
    numdata.tangent_residuals = asarray([c.tangent for c in constraints if c])
    numdata.xyz = xyz


def _is_converged_residuals(residuals: NDArray[(Any, 3), float64],
                            tol_res: float) -> bool:
    """Verify whether the maximum constraint residual is within tolerance."""
    if residuals is None or not residuals.any():
        return True
    max_res = max(norm(residuals, axis=1))
    return max_res < tol_res


def _is_converged_xyz(old_xyz: NDArray[(Any, 3), float64],
                      new_xyz: NDArray[(Any, 3), float64],
                      tol_xyz: float) -> bool:
    """Verify whether the maximum coordinate displacement
    between consecutive iterations is within tolerance.
    """
    max_dxyz = max(norm(new_xyz - old_xyz, axis=1))
    return max_dxyz < tol_xyz
