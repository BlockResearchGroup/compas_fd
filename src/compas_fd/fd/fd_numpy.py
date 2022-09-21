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
from numpy import zeros_like
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_fd.fd.result import Result


FloatNx3 = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Literal["*, 3"], Float64],
]


def fd_numpy(
    *,
    vertices: FloatNx3,
    fixed: List[int],
    edges: List[Tuple[int, int]],
    forcedensities: List[float],
    loads: Optional[FloatNx3] = None,
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
    C = connectivity_matrix(edges, "csr")
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
