from collections import namedtuple
from operator import itemgetter
from math import sin, cos, atan2, pi
from functools import wraps

from numpy import append, argsort, asarray, cross
from numpy.linalg import eig, inv

from compas.geometry import Frame, centroid_points, Rotation
from compas.geometry import Vector, angle_vectors_signed
from compas.utilities import pairwise

from compas_fd.nfd.math_utilities import euclidean_distance, arc_cos, is_isotropic, \
    transform_stress_angle, stress_vec_to_tensor, planar_rotation, transform_stress


__all__ = [
    'NaturalFace',
    'TriFace',
    'QuadFace',
    'NaturalEdge',
    'Goals',
    'mesh_preprocess'
]


# =================================================
# aliases
# =================================================

s, c = sin, cos


def s2(x):
    return s(x) * s(x)


def c2(x):
    return c(x) * c(x)


# =================================================
# decorators
# =================================================

def cache_iter(func):
    """Cache function result of the current iteration."""
    cached_func = '_c_' + func.__name__

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        res = self.cache.get(cached_func, None)
        if res is None:
            res = func(self, *args, **kwargs)
            self.cache[cached_func] = res
        return res
    return wrapper


def check_singularity(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError:
            raise Exception('Singularity in transformation matrix.')
    return wrapper


# =================================================
# natural geometry datastructures
# =================================================

class NaturalFace:
    """Represents geometry and natural stress data of a single face."""

    face_count = 0

    def __new__(cls, xyz, vertices_ids, stress_goal=None,
                stress_ref=None, is_subface=False):
        v = len(vertices_ids)
        if v == 3:
            return super().__new__(TriFace)
        elif v == 4:
            return super().__new__(QuadFace)
        else:
            raise ValueError('Only tri and quad faces can be processed, '
                             f'A face with {v} vertices was input.')

    def __init__(self, xyz, vertices_ids, stress_goal=None,
                 stress_ref=None, is_subface=False):
        self.cache = {}
        self._set_ids(vertices_ids, is_subface)
        self.xyz = xyz
        self.stress_ref = stress_ref
        self.stress_goal = stress_goal

    def update_xyz(self, xyz):
        self.cache.clear()
        self.xyz = xyz

    def _set_ids(self, vertices_ids, is_subface):
        self.vertices_ids = vertices_ids
        if is_subface:
            self.face_id = -1
        else:
            self.face_id = __class__.face_count
            __class__.face_count += 1

    def __len__(self):
        return len(self.vertices_ids)

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, xyz):
        self._xyz = [xyz[v] for v in self.vertices_ids]

    @property
    @cache_iter
    def stress_goal(self):
        if self.stress_ref is None or is_isotropic(self._stress_goal):
            return self._stress_goal
        return self._calc_stress_goal()

    @stress_goal.setter
    def stress_goal(self, goal):
        self._stress_goal = (1, 1, 0) if goal is None else goal
        if (not is_isotropic(self._stress_goal)) and (not self.stress_ref):
            raise ValueError("Non-isotropic stress state requires reference.")

    def _calc_stress_goal(self):
        """Calculate stress goal by intersection with plane
        defined by having reference vector as its normal."""
        f = self.frame
        g = self._stress_goal
        x, z, ref = f.xaxis, f.zaxis, asarray(self.stress_ref)
        x_r = cross(z, ref)
        θ = atan2(cross(x, x_r).dot(z), x.dot(x_r))
        return transform_stress_angle(g, θ)

    def transform_to_global(self, vec):
        """Transform vector from local face frame to global frame."""
        R = asarray(Rotation.from_frame(self.frame))[:3, :3]
        return R.dot(append(vec, .0))

    @cache_iter
    def principal_stress(self, to_global=False):
        """Principal stress values and vectors from local stresses."""
        s = stress_vec_to_tensor(self.stress)
        eigvals, eigvecs = eig(s)
        ids = argsort(-eigvals)
        eigvals, eigvecs = eigvals[ids], eigvecs[ids, :]
        if to_global:
            eigvecs = [self.transform_to_global(v) for v in eigvecs]
        return eigvals, eigvecs

    face_stresses = namedtuple('stresses', ['amplitudes', 'vectors'])

    @staticmethod
    def get_stresses(faces, xyz, s_calc):
        """Strategy for calculating stresses of multiple faces."""
        s = __class__.face_stresses
        if s_calc == -1:        # only tri (sub)face stresses
            return s(asarray(__class__._get_tris_attr(faces, 'stress')), None)
        if s_calc == 0:         # no stresses
            return s(None, None)
        if s_calc == 1:         # stresses in local frames
            return s(asarray([f.stress for f in faces]), None)
        if (s_calc in (2, 3)):  # principal stresses in local or global frame
            eigs = (f.principal_stress(to_global=(s_calc == 3)) for f in faces)
            return s(*map(list, zip(*eigs)))
        raise ValueError("s_calc must be set to {0, 1, 2, 3}.")

    @staticmethod
    def get_stress_goals(faces):
        """Get stress goals for multiple tri (sub)faces. For quad faces,
        transformation into tri subface frames is hence not required."""
        return asarray(__class__._get_tris_attr(faces, 'stress_goal'))

    @staticmethod
    def _get_tris_attr(faces, attr):
        """Get attribute for multiple tri (sub)faces."""
        attrs = []
        for f in faces:
            if len(f) == 3:
                attrs.append(getattr(f, attr, None))
            else:
                attrs.extend([getattr(t, attr, None)
                             for t in f.tri_faces])
        return attrs


class QuadFace(NaturalFace):
    """Represents geometry and natural stress data of a single quad face.
    A quad face is composed of 4 pairwise overlapping tri faces."""

    # vertex id sequence of each tri subface of the quad face
    __TRI_VERTICES = ((1, 3, 0), (3, 1, 2), (2, 0, 1), (0, 2, 3))

    def __init__(self, xyz, vertices_ids, stress_goal, stress_ref=None):
        super().__init__(xyz, vertices_ids, stress_goal, stress_ref)
        self._set_tri_faces(xyz)

    def update_xyz(self, xyz):
        """Update coordinates and geometric properties."""
        super().update_xyz(xyz)
        for t in self.tri_faces:
            t.update_xyz(xyz)

    def _set_tri_faces(self, xyz):
        tri_vertices_ids = (itemgetter(*self.__TRI_VERTICES[i])
                            (self.vertices_ids) for i in range(4))
        self.tri_faces = [TriFace(xyz, v_ids, self._stress_goal,
                          self.stress_ref, True) for v_ids in tri_vertices_ids]

    @property
    @cache_iter
    def area(self):
        return sum(t.area for t in self.tri_faces) / 2

    @property
    @cache_iter
    def frame(self):
        """Quad face frame, with origin at centroid and x-axis
        along midpoint of quad edge (1, 2)."""
        v0, v1, v2, v3 = self.xyz
        c0 = centroid_points(self.xyz)
        c1 = centroid_points((v1, v2))
        c2 = centroid_points((v2, v3))
        return Frame.from_points(c0, c1, c2)

    @property
    @cache_iter
    def rotations(self):
        """Planarized rotation matrices from quad face frame to each
        of the 4 tri subface frames. Quad system x-axis connects quad
        face centroid to midpoint of quad edge (1, 2)."""
        # angle of quad edge (0, 1) to quad x-axis
        vec_mid = self.frame.xaxis
        vec_edge = Vector.from_start_end(self.xyz[0], self.xyz[1])
        dθ = angle_vectors_signed(vec_edge, vec_mid, (0, 0, 1))

        # in-plane angles of tri subfaces axes to quad axes
        βa, γc = self.tri_faces[0].angles[1], self.tri_faces[2].angles[2]
        θa = pi - βa - dθ
        θb = -βa - dθ
        θc = γc - dθ
        θd = pi + γc - dθ
        return (planar_rotation(θ) for θ in (θa, θb, θc, θd))

    @property
    def force_densities(self):
        """6 natural force densities of a quad face for actual
        geometry and goal (2nd Piola-Kirchhoff) stresses."""
        na, nb, nc, nd = (t.force_densities for t in self.tri_faces)
        sum_force_densities = (na[1] + nc[0], nb[0] + nc[1], nb[1] + nd[0],
                               na[0] + nd[1], na[2] + nb[2], nc[2] + nd[2])
        return [n / 2 for n in sum_force_densities]

    @property
    @cache_iter
    def stress(self):
        """(2nd Piola-Kirchhoff) stresses at actual geometry."""
        tot_a = self.area * 2
        tris_a = (t.area for t in self.tri_faces)
        tris_s = (t.stress for t in self.tri_faces)
        quad_s = self._transform_stress_tris_to_quad(tris_s)
        return sum(a * s for a, s in zip(tris_a, quad_s)) / tot_a

    def _transform_stress_tris_to_quad(self, tris_stress):
        """Transform stresses from tri subfaces frames to quad frame."""
        return (transform_stress(s, R) for s, R
                in zip(tris_stress, self.rotations))


class TriFace(NaturalFace):
    """Represents geometry and natural stress data of a single tri face."""
    @property
    @cache_iter
    def frame(self):
        """Tri face frame, with origin at vertex 1 and x-axis edge (0, 1)."""
        return Frame.from_points(*self.xyz)

    @property
    @cache_iter
    def edge_lengths(self):
        vts_xyz = self.xyz[1:] + self.xyz[:2]
        return [euclidean_distance(u, v)
                for u, v in pairwise(vts_xyz)]

    @property
    @cache_iter
    def angles(self):
        l0, l1, l2 = self.edge_lengths
        α = arc_cos((l0 ** 2 + l1 ** 2 - l2 ** 2) / (2 * l0 * l1))
        β = arc_cos((l1 ** 2 + l2 ** 2 - l0 ** 2) / (2 * l1 * l2))
        γ = pi - α - β
        return (α, β, γ)

    @property
    @cache_iter
    def area(self):
        l0, l1, l2 = self.edge_lengths
        return l1 * l2 * sin(self.angles[1]) / 2

    @property
    @cache_iter
    def transformation(self):
        """3x3 transformation matrix for tri face stresses from local
        axis system into edge directions. The column vectors are unit
        edge stresses described in the local face frame."""
        α, β, γ = self.angles

        T = [[c2(γ),                c2(β),   1],
             [s2(γ),                s2(β),   0],
             [s(γ) * c(γ),   -s(β) * c(β),   0]]
        return asarray(T)

    @property
    @check_singularity
    def transformation_inv(self):
        """3x3 inverse transformation matrix for tri face stresses."""
        return inv(self.transformation)

    @property
    def force_densities(self):
        """3 natural force densities of a tri face for current
        geometry and goal 2nd Piola-Kirchhoff stresses."""
        a = self.area
        g = self.stress_goal
        Li2 = asarray([1 / (ln ** 2) for ln in self.edge_lengths])
        Ti = self.transformation_inv
        self._force_densities = a * Li2 * Ti.dot(g)
        return self._force_densities

    @property
    @cache_iter
    def stress(self):
        """2nd Piola-Kirchhoff stresses for current geometry."""
        L2 = asarray([ln ** 2 for ln in self.edge_lengths])
        a = self.area
        T = self.transformation
        n = self._force_densities  # force densities of previous geometry
        stress = (T * L2).dot(n) / a
        return stress


class NaturalEdge:
    """Represents geometry and force data of a single edge."""

    edge_count = 0

    def __new__(cls, xyz, vertices_ids, force_goal, fd_goal):
        cls.edge_count += 1
        if not (force_goal or fd_goal):
            return
        return super().__new__(cls)

    def __init__(self, xyz, vertices_ids, force_goal, fd_goal):
        self.cache = {}
        self.edge_id = __class__.edge_count - 1
        self.vertices_ids = tuple(vertices_ids)
        self.xyz = xyz
        self.force_goal = force_goal
        self.fd_goal = fd_goal

    def update_xyz(self, xyz):
        """Update coordinates and geometric properties."""
        self.cache.clear()
        self.xyz = xyz

    @property
    @cache_iter
    def length(self):
        return euclidean_distance(*self.xyz)

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, xyz):
        u, v = self.vertices_ids
        self._xyz = [xyz[u], xyz[v]]

    @property
    def force_density(self):
        """Get force density."""
        self._force_density = self.fd_goal or (self.force_goal / self.length)
        return self._force_density

    @property
    @cache_iter
    def force(self):
        """Calculate force for current geometry."""
        return self._force_density * self.length

    @staticmethod
    def get_forces(edges, xyz):
        """Get forces for multiple edges."""
        forces = [.0] * __class__.edge_count
        for edge in edges:
            forces[edge.edge_id] = edge.force
        return forces


# =================================================
# stress goals
# =================================================

class Goals:
    """Represents collection of geometric and stress resultant goals."""

    def __init__(self, mesh, stress, densities, forces, stress_ref=None):
        self.f_count = mesh.number_of_faces()
        self.stress = self._process_goal(stress, (1.0, 1.0, .0))
        self.densities = self._process_goal(densities)
        self.forces = self._process_goal(forces)
        self.stress_ref = stress_ref

    def _process_goal(self, goal, default=.0):
        return goal or [default for _ in range(self.f_count)]


# =================================================
# mesh data processing
# =================================================

def mesh_preprocess(mesh, goals):
    """Pre-process mesh to collections of natural elements."""
    # vertex indices mapping
    v_index = mesh.key_index()
    xyz = [mesh.vertex_coordinates(v) for v in mesh.vertices()]
    fixed = [mesh.key_index()[v] for v
             in mesh.vertices_where({'is_anchor': True})]
    edges_vts = ([v_index[u], v_index[v]] for u, v in mesh.edges())
    faces_vts = ([v_index[w] for w in mesh.face_vertices(f)]
                 for f in mesh.faces())

    # set natural faces and edges
    faces = [NaturalFace(xyz, face_vts, sp, goals.stress_ref)
             for face_vts, sp in zip(faces_vts, goals.stress)]
    edges = [e for e in [NaturalEdge(xyz, edge_vts, fp, qp)
             for edge_vts, fp, qp
             in zip(edges_vts, goals.forces, goals.densities)] if e]

    return faces, edges, xyz, fixed
