from typing import Tuple
from typing import List
from typing import Optional

from numpy import asarray
from numpy import zeros_like
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.topology import connectivity_matrix
from compas.geometry.linalg import normrow

from compas_fd.types import FloatNx3
from .result import Result


def fd_numpy(
    *,
    vertices: FloatNx3,
    fixed: List[int],
    edges: List[Tuple[int, int]],
    forcedensities: List[float],
    loads: Optional[FloatNx3] = None,
) -> Result:
    """Compute the equilibrium coordinates of a system of vertices connected by edges.

    Parameters
    ----------
    vertices : FloatNx3
        The XYZ coordinates of the vertices.
    fixed : list[int]
        The fixed vertices.
    edges : list[tuple[int, int]]
        The edges between the vertices.
    forcedensities : list[float]
        The force densities of the edges.
    loads : FloatNx3, optional
        The loads on the vertices.

    Returns
    -------
    Result

    See Also
    --------
    :func:`compas_fd.solvers.fd_constrained_numpy`

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_fd.solvers import fd_numpy

    >>> mesh = Mesh.from_meshgrid(dx=10, nx=10)

    >>> vertices = mesh.vertices_attributes("xyz")
    >>> fixed = list(mesh.vertices_where(vertex_degree=2))
    >>> edges = list(mesh.edges())
    >>> loads = [[0, 0, 0] for _ in range(len(vertices))]
    >>> q = [1.0] * len(edges)

    >>> result = fd_numpy(vertices=vertices, fixed=fixed, edges=edges, forcedensities=q, loads=loads)

    >>> all(result.residuals < 1e-6)
    True
    >>> all(result.forces > 0)
    True

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
