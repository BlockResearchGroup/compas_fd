from typing import Tuple
from typing import List
from typing import Optional

from scipy.sparse.linalg import spsolve
from compas.linalg import normrow

from compas_fd.types import FloatNx3
from .fd_numerical_data import FDNumericalData
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
    numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    b = numdata.p[numdata.free] - numdata.Af.dot(numdata.xyz[numdata.fixed])

    numdata.xyz[numdata.free] = spsolve(numdata.Ai, b)
    lengths = normrow(numdata.C.dot(numdata.xyz))
    forces = numdata.q * lengths
    residuals = numdata.p - numdata.A.dot(numdata.xyz)

    return Result(numdata.xyz, residuals, forces, lengths)
