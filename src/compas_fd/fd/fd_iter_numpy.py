from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from numpy import float64

from ..result import Result
from ..constraints import Constraint
from ..numdata import FDNumericalData
from ..solvers import FDConstraintSolver


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
    solver = FDConstraintSolver(numdata, constraints, max_iter, tol_res, tol_dxyz)
    result = solver()
    return result