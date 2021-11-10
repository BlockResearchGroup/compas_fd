from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from dataclasses import astuple

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
                  max_iter: int = 100, tol_res: float = 1E-3, tol_xyz: float = 1E-3
                  ) -> Result:
    """Iteratively compute the equilibrium coordinates of a system of vertices connected by edges.
    Vertex constraints are recomputed at each iteration.
    """
    nd = FDNumericalData.from_fd_params(vertices, fixed, edges, forcedensities, loads)

    for k in range(max_iter):
        _xyz = nd.xyz
        _solve_fd(nd)
        _update_constraints(nd, constraints)
        if (_is_converged_res(nd.tr, tol_res) and
           _is_converged_xyz(_xyz, nd.xyz, tol_xyz)):
            break

    return nd.to_result()


def _solve_fd(num_data: FDNumericalData
              ) -> None:
    """Solve a single iteration for the equilibrium coordinates of a system.
    All updated numerical arrays are stored in the num_data parameter.
    """
    free, fixed, xyz, q, Q, p, C, Ai, Af, *_ = astuple(num_data)
    b = p[free] - Af.dot(xyz[fixed])
    xyz[free] = spsolve(Ai, b)
    lengths = normrow(C.dot(xyz))
    num_data.f = q * lengths
    num_data.r = p - C.T.dot(Q).dot(C).dot(xyz)
    num_data.ln = lengths
    num_data.xyz = xyz


def _update_constraints(num_data: FDNumericalData,
                        constraints: Sequence[Constraint]
                        ) -> None:
    """Update all vertex constraints by the residuals of the current iteration,
    and store their updated vertex coordinates in the num_data parameter.
    """
    xyz = num_data.xyz
    residuals = num_data.r
    for vertex, constraint in enumerate(constraints):
        if not constraint:
            continue
        constraint.location = xyz[vertex]
        constraint.residual = residuals[vertex]
        xyz[vertex] = constraint.location + constraint.tangent * 0.5
    num_data.tr = asarray([c.tangent for c in constraints if c])
    num_data.xyz = xyz


def _is_converged_res(residuals: NDArray[(Any, 3), float64],
                      tol_res: float
                      ) -> bool:
    """Validate whether the maximum constraint residual is within tolerance.
    """
    max_res = max(norm(residuals, axis=1))
    return max_res < tol_res


def _is_converged_xyz(old_xyz: NDArray[(Any, 3), float64],
                      new_xyz: NDArray[(Any, 3), float64],
                      tol_xyz: float
                      ) -> bool:
    """Validate whether the maximum coordinate displacement
    between consecutive iterations is within tolerance.
    """
    max_dxyz = max(norm(new_xyz - old_xyz, axis=1))
    return max_dxyz < tol_xyz
