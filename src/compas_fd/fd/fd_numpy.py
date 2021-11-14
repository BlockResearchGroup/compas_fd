from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from numpy import float64

from compas_fd.result import Result
from compas_fd.numdata import FDNumericalData
from compas_fd.solvers import FDSolver


def fd_numpy(*,
             vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
             fixed: List[int],
             edges: List[Tuple[int, int]],
             force_densities: List[float],
             loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None,
             ) -> Result:
    """
    Compute the equilibrium coordinates of a system of vertices connected by edges.
    """
    numdata = FDNumericalData(vertices, fixed, edges, force_densities, loads)
    solver = FDSolver(numdata)
    result = solver()
    return result
