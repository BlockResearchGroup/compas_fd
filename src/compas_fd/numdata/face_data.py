from typing import Any
from typing import List
from typing import Tuple
from nptyping import NDArray

from numpy import add
from numpy import cross
from numpy import float64
from numpy import roll
from numpy import zeros
from numpy.linalg import norm
from scipy.sparse import coo_matrix

from compas.datastructures import Mesh
from compas.numerical import face_matrix
from .numerical_data import lazy_eval


class FaceDataMixin:
    """Stores numerical mesh face data.
    Use as mixin for NumericalData classes.
    """

    def __init__(self, mesh: Mesh) -> None:
        self.faces_vertices = mesh
        self.reset_face_data()

    def reset_face_data(self) -> None:
        self._tributary_area_matrix = None
        self._face_areas = None
        self._face_normals = None
        self._face_centroids = None
        self._face_cross_products = None

    @property
    def faces_vertices(self) -> List[Tuple[int]]:
        return self._faces_vertices

    @faces_vertices.setter
    def faces_vertices(self, mesh: Mesh) -> None:
        v_i = mesh.vertex_index()
        f_i = {fkey: index for index, fkey in enumerate(mesh.faces())}
        faces_vertices = [None] * mesh.number_of_faces()
        for f in mesh.faces():
            faces_vertices[f_i[f]] = [v_i[v] for v in mesh.face_vertices(f)]
        self._faces_vertices = faces_vertices
        self._face_matrix = None

    @property
    @lazy_eval
    def face_matrix(self) -> NDArray[(Any, Any), float64]:
        return face_matrix(self.faces_vertices, rtype='csr', normalize=True)

    @property
    @lazy_eval
    def tributary_area_matrix(self) -> NDArray[(Any, Any), float64]:
        """Tributary areas matrix as a sparse (vertices x faces) array.
        Entry a_ij holds tributary area of face j for vertex i.
        """
        v_count = self.xyz.shape[0]
        f_count = len(self.faces_vertices)
        data = []
        rows = []
        cols = []

        for face, fcp in enumerate(self.face_cross_products):
            face_vertices = self.faces_vertices[face]
            partial_areas = norm(fcp, axis=1)
            tributary_areas = partial_areas + roll(partial_areas, -1)
            data.extend(tributary_areas)
            rows.extend(face_vertices)
            cols.extend([face] * len(face_vertices))

        return coo_matrix((data, (rows, cols)), (v_count, f_count)).tocsr() * 0.25

    @property
    @lazy_eval
    def face_areas(self) -> NDArray[(Any, 1), float64]:
        return self.tributary_area_matrix.sum(axis=0).reshape((-1, 1))

    @property
    @lazy_eval
    def face_normals(self) -> NDArray[(Any, 1), float64]:
        f_count = len(self.faces_vertices)
        face_normals = zeros((f_count, 3), dtype=float)
        for face, fcp in enumerate(self.face_cross_products):
            face_normals[face, :] = add.reduce(fcp)
        face_normals /= norm(face_normals, axis=1)[:, None]
        return face_normals

    @property
    @lazy_eval
    def face_centroids(self) -> NDArray[(Any, 1), float64]:
        return self.F.dot(self.xyz)

    @property
    @lazy_eval
    def face_cross_products(self) -> List[NDArray[(Any, 3), float64]]:
        """Cross products of the consecutive (centroid -> vertex)
        vectors for each of the vertices of the face.
        """
        face_cross_products = []
        centroids = self.face_centroids
        for face, face_vertices in enumerate(self.faces_vertices):
            vecs = self.xyz[face_vertices] - centroids[face]
            vecs_shift = roll(vecs, -1, axis=0)
            face_cross_products.append(cross(vecs, vecs_shift))
        return face_cross_products

    # aliases
    F = face_matrix
    TA = tributary_area_matrix
    fa = face_areas
    fn = face_normals
    fc = face_centroids
    fcp = face_cross_products
