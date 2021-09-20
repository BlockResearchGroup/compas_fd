from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from numpy import asarray, zeros_like
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from .result import Result


def fd_numpy(*,
             vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
             fixed: List[int],
             edges: List[Tuple[int, int]],
             forcedensities: List[float],
             loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None,
             ) -> Result:
    """
    Compute the equilibrium coordinates of a system of vertices connected by edges.
    """
    v = len(vertices)
    free = list(set(range(v)) - set(fixed))
    xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
    q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
    if loads is None:
        p = zeros_like(xyz)
    else:
        p = asarray(loads, dtype=float64).reshape((-1, 3))
    C = connectivity_matrix(edges, 'csr')
    Ci = C[:, free]
    Cf = C[:, fixed]
    Ct = C.transpose()
    Cit = Ci.transpose()
    Q = diags([q.flatten()], [0])
    A = Cit.dot(Q).dot(Ci)
    b = p[free] - Cit.dot(Q).dot(Cf).dot(xyz[fixed])
    xyz[free] = spsolve(A, b)
    lengths = normrow(C.dot(xyz))
    forces = q * lengths
    residuals = p - Ct.dot(Q).dot(C).dot(xyz)
    return Result(xyz, residuals, forces, lengths)
