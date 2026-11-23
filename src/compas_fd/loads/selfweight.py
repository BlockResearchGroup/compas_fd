from typing import cast

import numpy
import scipy.sparse
from compas.datastructures import Mesh
from compas.linalg import cross_vectors
from compas.linalg import face_matrix
from compas.linalg import length_vector

from compas_fd._scipy import dot_coordinates
from compas_fd.types import FloatArray
from compas_fd.types import FloatNx3


class SelfweightCalculator:
    """Compute mesh vertex self-weight from tributary area, thickness and density.

    After construction, the calculator provides a callable that can be used
    to compute the selfweight for the current mesh coordinates.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The mesh representing a surface structure.
    density : float, optional
        Weight per unit volume, in consistent force and length units.
    thickness_attr_name : str, optional
        The name of the vertex attribute storing the surface thickness.

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_fd.loads import SelfweightCalculator
    >>> mesh = Mesh.from_meshgrid(dx=10, nx=10)
    >>> mesh.update_default_vertex_attributes(t=0.10)
    >>> density = 22
    >>> calculator = SelfweightCalculator(mesh, density=density)
    >>> xyz = mesh.vertices_attributes("xyz")
    >>> selfweight = calculator(xyz)
    >>> len(selfweight) == mesh.number_of_vertices()
    True
    >>> bool(abs(selfweight[0, 0] - 0.25 * 0.10 * density) < 1e-12)
    True

    """

    def __init__(
        self,
        mesh: Mesh,
        density: float = 1.0,
        thickness_attr_name: str = "t",
    ) -> None:
        self.mesh: Mesh = mesh
        self.rho: FloatArray = numpy.array([t * density for t in mesh.vertices_attribute(thickness_attr_name)]).reshape((-1, 1))
        self.vertex_index: dict[int, int] = mesh.vertex_index()
        self.fvertex_index: dict[int, int] = {fkey: index for index, fkey in enumerate(mesh.faces())}
        self.is_loaded: dict[int, bool] = {fkey: True for fkey in mesh.faces()}
        self.F = self.compute_face_matrix()

    def __call__(self, xyz: FloatNx3) -> FloatArray:
        """Return weights of shape `(n, 1)` in mesh vertex order."""
        ta = self.compute_tributary_areas(numpy.asarray(xyz))
        return ta * self.rho

    def compute_face_matrix(self) -> scipy.sparse.csr_matrix:
        """Compute the face matrix of the mesh.

        Returns
        -------
        scipy.sparse.csr_matrix
            One row per face and one column per incident vertex index. Each
            nonzero entry is the reciprocal of that face's vertex count.

        """
        face_vertices: list[list[int]] = [[] for _ in range(self.mesh.number_of_faces())]
        for fkey in self.mesh.faces():
            face_vertices[self.fvertex_index[fkey]] = [self.vertex_index[key] for key in self.mesh.face_vertices(fkey)]
        return cast(scipy.sparse.csr_matrix, face_matrix(face_vertices, rtype="csr", normalize=True))

    def compute_tributary_areas(self, xyz: FloatArray) -> FloatArray:
        """Compute the tributary area of each vertex for the current coordinates.

        Parameters
        ----------
        xyz : numpy.ndarray
            Vertex coordinates of shape `(n, 3)` in mesh vertex order.

        Returns
        -------
        numpy.ndarray
            Tributary areas of shape `(n, 1)`, in squared coordinate units.

        """
        mesh = self.mesh
        vertex_index = self.vertex_index
        fvertex_index = self.fvertex_index
        is_loaded = self.is_loaded

        C = dot_coordinates(self.F, xyz)

        areas = numpy.zeros((xyz.shape[0], 1))

        for u in mesh.vertices():
            p0 = xyz[vertex_index[u]]

            a = 0
            for v in mesh.halfedge[u]:
                p1 = xyz[vertex_index[v]]
                p01 = p1 - p0

                fkey = mesh.halfedge[u][v]
                if fkey is not None and is_loaded[fkey]:
                    p2 = C[fvertex_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p2 - p0))

                fkey = mesh.halfedge[v][u]
                if fkey is not None and is_loaded[fkey]:
                    p3 = C[fvertex_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p3 - p0))

            areas[vertex_index[u]] = a

        return areas
