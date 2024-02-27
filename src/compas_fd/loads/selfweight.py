import numpy
import scipy.sparse
from compas.datastructures import Mesh
from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.matrices import face_matrix

from compas_fd.types import FloatNx1
from compas_fd.types import FloatNx3


class SelfweightCalculator:
    """Class for computing the selfweight of a mesh representing a surface structure
    with a specific density and thickness.

    After construction, the calculator provides a callable that can be used
    to compute the selfweight for the current mesh coordinates.

    Parameters
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        The mesh representing a surface structure.
    density : float, optional
        The density of the surface material.
    thickness_attr_name : str, optional
        The name of the vertex attribute storing the surface thickness.

    Examples
    --------
    >>> from compas.datastructures import Mesh
    >>> from compas_fd.loads import SelfWeightCalculator
    >>> mesh = Mesh.from_meshgrid(dx=10, nx=10)
    >>> mesh.update_default_vertex_attributes(t=0.10)
    >>> density = 22
    >>> calculator = SelfweightCalculator(mesh, density=density)
    >>> xyz = mesh.vertices_attributes("xyz")
    >>> selfweight = calculator(xyz)
    >>> len(selfweight) == mesh.number_of_vertices()
    True
    >>> selfweight[0] == 0.25 * density
    True

    """

    def __init__(
        self,
        mesh: Mesh,
        density: float = 1.0,
        thickness_attr_name: str = "t",
    ):
        self.mesh = mesh
        self.rho = numpy.array([t * density for t in mesh.vertices_attribute(thickness_attr_name)]).reshape((-1, 1))
        self.vertex_index = mesh.vertex_index()
        self.fvertex_index = {fkey: index for index, fkey in enumerate(mesh.faces())}
        self.is_loaded = {fkey: True for fkey in mesh.faces()}
        self.F = self.compute_face_matrix()

    def __call__(self, xyz: FloatNx3) -> FloatNx1:
        ta = self.compute_tributary_areas(numpy.asarray(xyz))
        return ta * self.rho

    def compute_face_matrix(self) -> scipy.sparse.csr_matrix:
        """Compute the face matrix of the mesh.

        Returns
        -------
        :class:`scipy.sparse.csr_matrix`
            Number of rows is equal to the number of faces.
            Number of columns is equal to the number of vertices.
            Each row representa a face.
            The row contains ones in every column corresponding to a vertex of the face.

        """
        face_vertices = [None] * self.mesh.number_of_faces()
        for fkey in self.mesh.faces():
            face_vertices[self.fvertex_index[fkey]] = [self.vertex_index[key] for key in self.mesh.face_vertices(fkey)]
        return face_matrix(face_vertices, rtype="csr", normalize=True)

    def compute_tributary_areas(self, xyz: FloatNx3) -> FloatNx1:
        """Compute the tributary are of every vertex for the current coordinates.

        Parameters
        ----------
        xyz : FloatNx3
            The vertex coordinates.

        Returns
        -------
        FloatNx1
            The tributary are per vertex.

        """
        mesh = self.mesh
        vertex_index = self.vertex_index
        fvertex_index = self.fvertex_index
        is_loaded = self.is_loaded

        C = self.F.dot(xyz)

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
