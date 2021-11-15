from numpy import add
from numpy import cross
from numpy import roll
from numpy import zeros
from numpy.linalg import norm
from scipy.sparse import coo_matrix

from compas.datastructures import Mesh
from compas.numerical import face_matrix


class FaceDataMixin:
    """Stores numerical mesh face data.
    Use as mixin for NumericalData classes.
    """

    def __init__(self, mesh: Mesh):
        self.faces_vertices = mesh
        self.reset_face_data()

    def reset_face_data(self):
        self._tributary_area_matrix = None
        self._face_areas = None
        self._face_normals = None
        self._face_centroids = None
        self._face_cross_products = None

    @property
    def faces_vertices(self):
        return self._faces_vertices

    @faces_vertices.setter
    def faces_vertices(self, mesh: Mesh):
        v_i = mesh.vertex_index()
        f_i = {fkey: index for index, fkey in enumerate(mesh.faces())}
        faces_vertices = [None] * mesh.number_of_faces()
        for f in mesh.faces():
            faces_vertices[f_i[f]] = [v_i[v] for v in mesh.face_vertices(f)]
        self._faces_vertices = faces_vertices
        self._face_matrix = None

    @property
    def face_matrix(self):
        if self._face_matrix is None:
            self._face_matrix = face_matrix(self.faces_vertices, rtype='csr', normalize=True)
        return self._face_matrix

    @property
    def tributary_area_matrix(self):
        """Tributary areas matrix as a sparse (vertices x faces) array.
        Entry a_ij holds tributary area of face j for vertex i.
        """
        if self._tributary_area_matrix is None:
            self._compute_tributary_area_matrix()
        return self._tributary_area_matrix

    def _compute_tributary_area_matrix(self):
        v_count = self.xyz.shape[0]
        f_count = len(self.faces_vertices)
        data = []
        rows = []
        cols = []

        for face, fcp in enumerate(self.face_cross_products):
            face_vertices = self.faces_vertices[face]
            partial_areas = norm(fcp, axis=1)
            tributary_area = partial_areas + roll(partial_areas, -1)
            data.extend(tributary_area)
            rows.extend(face_vertices)
            cols.extend([face] * len(face_vertices))

        self._tributary_area_matrix = coo_matrix((data, (rows, cols)),
                                                 (v_count, f_count)).tocsr() * 0.25

    @property
    def face_areas(self):
        if self._face_areas is None:
            self._face_areas = self.tributary_area_matrix.sum(axis=0).reshape((-1, 1))
        return self._face_areas

    @property
    def face_normals(self):
        if self._face_normals is None:
            self._compute_face_normals()
        return self._face_normals

    def _compute_face_normals(self):
        f_count = len(self.faces_vertices)
        self._face_normals = zeros((f_count, 3), dtype=float)
        for face, fcp in enumerate(self.face_cross_products):
            self._face_normals[face, :] = add.reduce(fcp)
        self._face_normals /= norm(self._face_normals, axis=1)[:, None]

    @property
    def face_centroids(self):
        if self._face_centroids is None:
            self._face_centroids = self.F.dot(self.xyz)
        return self._face_centroids

    @property
    def face_cross_products(self):
        """Cross products of the consecutive (centroid -> vertex)
        vectors for each of the vertices of the face.
        """
        if self._face_cross_products is None:
            self._compute_face_cross_products()
        return self._face_cross_products

    def _compute_face_cross_products(self):
        self._face_cross_products = []
        centroids = self.face_centroids
        for face, face_vertices in enumerate(self.faces_vertices):
            vecs = self.xyz[face_vertices] - centroids[face]
            vecs_shift = roll(vecs, -1, axis=0)
            self._face_cross_products.append(cross(vecs, vecs_shift))

    # aliases
    F = face_matrix
    TA = tributary_area_matrix
    fa = face_areas
    fn = face_normals
    fc = face_centroids
    fcp = face_cross_products
