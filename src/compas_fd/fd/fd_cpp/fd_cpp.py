from typing import Optional, Sequence
from typing_extensions import Annotated

from ..result import Result
from .fdm import fd_solve   # win64 build


def fd_cpp(*,
           vertices: Sequence[Annotated[Sequence[float], 3]],
           fixed: Sequence[int],
           edges: Sequence[Annotated[Sequence[int], 2]],
           force_densities: Sequence[float],
           loads: Optional[Sequence[Annotated[Sequence[float], 3]]] = None
           ) -> Result:
    """Compute the equilibrium conditions by the force density method.
    The algorithms backend is implemented in C++ through pybind."""
    return Result(*fd_solve(vertices, fixed, edges, force_densities, loads))
