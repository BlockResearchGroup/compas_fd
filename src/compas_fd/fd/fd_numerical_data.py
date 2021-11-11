from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from dataclasses import dataclass
from dataclasses import astuple

from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import diags

from compas.numerical import connectivity_matrix

from .result import Result


@dataclass
class FDNumericalData:
    """Stores numerical data used by the force density algorithms."""
    free: int
    fixed: int
    xyz: NDArray[(Any, 3), float64]
    C: NDArray[(Any, Any), int]
    q: NDArray[(Any, 1), float64]
    Q: NDArray[(Any, Any), float64]
    p: NDArray[(Any, 1), float64]
    A: NDArray[(Any, Any), float64]
    Ai: NDArray[(Any, Any), float64]
    Af: NDArray[(Any, Any), float64]
    forces: NDArray[(Any, 1), float64] = None
    lengths: NDArray[(Any, 1), float64] = None
    residuals: NDArray[(Any, 3), float64] = None
    tangent_residuals: NDArray[(Any, 3), float64] = None
    normal_residuals: NDArray[(Any, 1), float64] = None

    def __iter__(self):
        return iter(astuple(self))

    @classmethod
    def from_params(cls,
                    vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
                    fixed: List[int],
                    edges: List[Tuple[int, int]],
                    forcedensities: List[float],
                    loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None):
        """Construct numerical arrays from force density solver input parameters."""
        free = list(set(range(len(vertices))) - set(fixed))
        xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        C = connectivity_matrix(edges, 'csr')
        Ci = C[:, free]
        Cf = C[:, fixed]
        q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
        Q = diags([q.flatten()], [0])
        p = (zeros_like(xyz) if loads is None else
             asarray(loads, dtype=float64).reshape((-1, 3)))
        A = C.T.dot(Q).dot(C)
        Ai = Ci.T.dot(Q).dot(Ci)
        Af = Ci.T.dot(Q).dot(Cf)
        return cls(free, fixed, xyz, C, q, Q, p, A, Ai, Af)

    @classmethod
    def from_mesh(cls, mesh):
        """Construct numerical arrays from input mesh."""
        raise NotImplementedError

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        return Result(self.xyz, self.residuals, self.forces, self.lengths)
