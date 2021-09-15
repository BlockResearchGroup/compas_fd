from numpy import array
from numpy import zeros

from compas.geometry import cross_vectors
from compas.geometry import length_vector
from compas.numerical import face_matrix


class SelfweightCalculator:

    def __init__(self, mesh, density=1.0, thickness_attr_name='t'):
        self.mesh = mesh
        self.rho = array([t * density for t in mesh.vertices_attribute(thickness_attr_name)]).reshape((-1, 1))
        self.key_index = mesh.key_index()
        self.fkey_index = {fkey: index for index, fkey in enumerate(mesh.faces())}
        self.is_loaded = {fkey: True for fkey in mesh.faces()}
        self.F = self.face_matrix()

    def __call__(self, xyz):
        ta = self._tributary_areas(xyz)
        return ta * self.rho

    def face_matrix(self):
        face_vertices = [None] * self.mesh.number_of_faces()
        for fkey in self.mesh.faces():
            face_vertices[self.fkey_index[fkey]] = [self.key_index[key] for key in self.mesh.face_vertices(fkey)]
        return face_matrix(face_vertices, rtype='csr', normalize=True)

    def _tributary_areas(self, xyz):
        mesh = self.mesh
        key_index = self.key_index
        fkey_index = self.fkey_index
        is_loaded = self.is_loaded

        C = self.F.dot(xyz)

        areas = zeros((xyz.shape[0], 1))
        for u in mesh.vertices():
            p0 = xyz[key_index[u]]

            a = 0
            for v in mesh.halfedge[u]:
                p1 = xyz[key_index[v]]
                p01 = p1 - p0

                fkey = mesh.halfedge[u][v]
                if fkey is not None and is_loaded[fkey]:
                    p2 = C[fkey_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p2 - p0))

                fkey = mesh.halfedge[v][u]
                if fkey is not None and is_loaded[fkey]:
                    p3 = C[fkey_index[fkey]]
                    a += 0.25 * length_vector(cross_vectors(p01, p3 - p0))

            areas[key_index[u]] = a

        return areas
