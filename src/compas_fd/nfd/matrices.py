from numpy import asarray, copy, zeros, ix_
from scipy.sparse import coo_matrix

from compas.geometry import Rotation


__all__ = [
    'StiffnessMatrixAssembler',
    'LoadMatrixAssembler'
]


class StiffnessMatrixAssembler:
    """Represents assembly of a global force density stiffness matrix.
    A new instance of StiffnessMatrixAssembler should be generated at each
    solver iteration, so that the stiffness matrix is rebuilt completely.

    Parameters
    ----------
    free : sequence of int
        The indices of free mesh vertices.
    fixed : sequence of int
        The indices of fixed mesh vertices.
    edges : iterable of :class:`NaturalEdge`
        The processed edges of the mesh.
    faces : iterable of :class:`NaturalFace`
        The processed faces of the mesh.

    Attributes
    ----------
    matrix : ndarray
        The full stiffness matrix as a 2D array.
    free_matrix : ndarray
        The stiffness matrix of free vertices as a 2D array.
    fixed_matrix : ndarray
        The stiffness matrix of fixed vertices as a 2D array.
    """

    def __init__(self, free, fixed, edges, faces):
        self.free = free
        self.fixed = fixed

        self.data = []
        self.rows = []
        self.cols = []

        self._add_faces(faces)
        self._add_edges(edges)

        v_count = len(free + fixed)
        self._mat = coo_matrix((self.data, (self.rows, self.cols)),
                               (v_count, v_count)).tocsr()

    def _add_faces(self, faces):
        for face in faces:
            fv_count = len(face)
            if fv_count == 3:
                self._add_tri_face(face)
            elif fv_count == 4:
                self._add_quad_face(face)

    def _add_tri_face(self, face):
        v0, v1, v2 = face.vertices_ids
        n0, n1, n2 = face.force_densities
        self.data += [n1 + n2, -n2, -n1,
                      -n2, n0 + n2, -n0,
                      -n1, -n0, n0 + n1]
        self.rows += [v0] * 3 + [v1] * 3 + [v2] * 3
        self.cols += [v0, v1, v2] * 3

    def _add_quad_face(self, face):
        v0, v1, v2, v3 = face.vertices_ids
        n0, n1, n2, n3, n4, n5 = face.force_densities
        self.data += [n0 + n3 + n5, -n0, -n5, -n3,
                      -n0, n0 + n1 + n4, -n1, -n4,
                      -n5, -n1, n1 + n2 + n5, -n2,
                      -n3, -n4, -n2, n2 + n3 + n4]
        self.rows += [v0] * 4 + [v1] * 4 + [v2] * 4 + [v3] * 4
        self.cols += [v0, v1, v2, v3] * 4

    def _add_edges(self, edges):
        for edge in edges:
            v0, v1 = edge.vertices_ids
            n = edge.force_density
            self.data += [n, n, -n, -n]
            self.rows += [v0, v1, v0, v1]
            self.cols += [v0, v1, v1, v0]

    @property
    def matrix(self):
        return self._mat

    @property
    def free_matrix(self):
        return self._mat[ix_(self.free, self.free)]

    @property
    def fixed_matrix(self):
        return self._mat[ix_(self.free, self.fixed)]


class LoadMatrixAssembler:
    """Represents assembly of a global load matrix.

    Parameters
    ----------
    vertices : sequence of int
        The indices of mesh vertices.
    faces : iterable of :class:`NaturalFace`
        The processed faces of the mesh.
    vertex_loads : sequence of tuple
        The loads on the mesh vertices in global XYZ directions.
    global_face_loads : sequence of tuple of float
        The loads on the mesh faces in global XYZ directions.
    local_face_loads : sequence of tuple of float
        The loads on the mesh faces in local face XYZ directions.
        Local loads get converted to global loads by rotation
        from the local face frames.

    Attributes
    ----------
    matrix : ndarray
        The full load matrix as a 2D array.

    Notes
    -----
    A LoadMatrixAssembler is to be instantiated once per session and to persist
    over iterations. By calling instance method update(), the intenral matrix
    is updated corresponding to the geometry of the latest state.
    """

    def __init__(self, vertices, faces, vertex_loads=None,
                 global_face_loads=None, local_face_loads=None):
        self.faces = faces
        self._vertices_mat = self._load_mat(vertex_loads, zeros((len(vertices), 3)))
        self._gfl = self._load_mat(global_face_loads)
        self._lfl = self._load_mat(local_face_loads)
        self._has_face_loads = ((self._gfl is not None) or (self._lfl is not None))
        self._mat = self._vertices_mat
        self.update()

    @property
    def matrix(self):
        return self._mat

    def _load_mat(self, loads, default=None):
        """Pre-process load matrices of each element type."""
        return asarray(loads).reshape(-1, 3) if loads is not None else default

    def update(self):
        """Assemble all loads corresponding to current geometry into updated load matrix.
        To be called at each iteration where geometry has been updated."""
        if not self._has_face_loads:
            return self._mat
        self._mat = copy(self._vertices_mat)
        if self._gfl is not None:
            self._add_face_loads(local=False)
        if self._lfl is not None:
            self._add_face_loads(local=True)

    def _add_face_loads(self, local=False):
        face_loads = self._lfl if local else self._gfl
        for face, face_load in zip(self.faces, face_loads):
            vertex_load = face_load * (face.area / len(face))
            if local:
                R = asarray(Rotation.from_frame(face.frame))[:3, :3]
                vertex_load = R.dot(vertex_load)
            self._mat[face.vertices_ids, :] += vertex_load

    def _add_edge_loads(self):
        raise NotImplementedError
