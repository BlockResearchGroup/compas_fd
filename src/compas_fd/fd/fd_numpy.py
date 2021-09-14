from typing import List, Tuple, NamedTuple
from typing_extensions import Annotated

from collections import namedtuple

from numpy import asarray
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_fd.loads import SelfweightCalculator


Vector3 = Annotated[List[float], 3]

Result = NamedTuple('Result', [
    ('vertices', List[Vector3]),
    ('forces', List[float]),
    ('lenghts', List[float]),
    ('residuals', List[Vector3])
])


def fd_numpy(*,
             vertices: List[Vector3],
             edges: List[Tuple[int, int]],
             loads: List[Vector3],
             q: List[float],
             fixed: List[int]) -> Result:
    """
    Compute the equilibrium coordinates of a system of vertices connected by edges.
    """
    v = len(vertices)
    free = list(set(range(v)) - set(fixed))
    xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
    q = asarray(q, dtype=float64).reshape((-1, 1))
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
    lengths = normrow(C.dot(xyz))  # noqa: E741
    forces = q * lengths
    residuals = p - Ct.dot(Q).dot(C).dot(xyz)
    return Result('result', [xyz, forces, lengths, residuals])
