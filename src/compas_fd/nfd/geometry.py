from __future__ import annotations

from typing import Any, Callable, Generator, List, Sequence, Tuple, NamedTuple
from typing_extensions import Annotated
from nptyping import NDArray

from collections import namedtuple
from operator import itemgetter
from math import sin, cos, atan2, pi
from functools import wraps

from numpy import append, argsort, asarray, cross, float64
from numpy.linalg import eig, inv

from compas.datastructures import Mesh
from compas.geometry import Frame, centroid_points, Rotation
from compas.geometry import Vector, angle_vectors_signed
from compas.utilities import pairwise

from .math_utilities import euclidean_distance, arc_cos, is_isotropic, \
     transform_stress_angle, stress_vec_to_tensor, planar_rotation, transform_stress
from .goals import Goals


Vec = Annotated[Sequence[float], 3]
NpVec = NDArray[(3,), float64]
VertexArray = NDArray[(Any, 3), float64]


__all__ = [
    'NaturalFace',
    'TriFace',
    'QuadFace',
    'NaturalEdge',
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

def cache_iter(func: Callable) -> Callable:
    """Cache a method return value of the current iteration in the cache dictionary
    of its class instance. After being cached, subsequent calls to the method will
    return the stored result, until the cache dictionary is explicitely cleared."""
    cached_func = '_c_' + func.__name__

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        res = self.cache.get(cached_func, None)
        if res is None:
            res = func(self, *args, **kwargs)
            self.cache[cached_func] = res
        return res
    return wrapper


def check_singularity(func: Callable) -> Callable:
    """Verify if a numerical error occurred in the method call due to zero division."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError:
            raise Exception('Singularity in transformation matrix.')
    return wrapper


# =================================================
# natural geometry
# =================================================

class NaturalEdge:
    """Represents geometry and force data of a single edge.

    Parameters
    ----------
    mesh_xyz : ndarray of float
        XYZ vertex coordinates of the whole mesh as a (n, 3) array.
    vertices_ids : sequence of int
        Sequence of contiguous vertex indices.
    force_goal : float
        Goal force for the edge.
    force_density_goal : float
        Goal force density for the edge, overwrites force goals.

    Attributes
    ----------
    edge_count : int
        The number of instantiated NaturalEdges.
    xyz : ndarray of float
        XYZ vertex coordinates of the edge as a (2, 3) array.
    length: float
        Length of edge.
    force_density: float
        Force density in edge for current geometry.
    force : float
        Force in edge for current geometry.
    """

    edge_count = 0

    def __new__(cls, mesh_xyz, vertices_ids, force_goal, force_density_goal):
        cls.edge_count += 1
        if not (force_goal or force_density_goal):
            return
        return super().__new__(cls)

    def __init__(self, mesh_xyz: VertexArray, vertices_ids: Sequence[int],
                 force_goal: float = None, force_density_goal: float = None) -> None:
        self.cache = {}
        self.edge_id = __class__.edge_count - 1
        self.vertices_ids = tuple(vertices_ids)
        self.xyz = mesh_xyz
        self.force_goal = force_goal
        self.force_density_goal = force_density_goal

    def update_xyz(self, mesh_xyz: VertexArray) -> None:
        """Update XYZ edge coordinates and clear geometry cache."""
        self.cache.clear()
        self.xyz = mesh_xyz

    @property
    @cache_iter
    def length(self) -> float:
        """Edge length from euclidean distance of vertces."""
        return euclidean_distance(*self.xyz)

    @property
    def xyz(self) -> NDArray[(2, 3), float64]:
        """XYZ vertex coordinates of the edge."""
        return self._xyz

    @xyz.setter
    def xyz(self, mesh_xyz: VertexArray) -> None:
        u, v = self.vertices_ids
        self._xyz = (mesh_xyz[u], mesh_xyz[v])

    @property
    def force_density(self) -> float:
        """Force density in edge for current geometry."""
        self._force_density = self.force_density_goal or (self.force_goal / self.length)
        return self._force_density

    @property
    @cache_iter
    def force(self) -> float:
        """Force in edge for current geometry."""
        return self._force_density * self.length

    @classmethod
    def get_forces(cls, edges: Sequence[NaturalEdge]) -> List[float]:
        """Get forces for sequence of edges."""
        forces = [.0] * cls.edge_count
        for edge in edges:
            forces[edge.edge_id] = edge.force
        return forces

    @classmethod
    def get_lengths(cls, edges: Sequence[NaturalEdge]) -> List[float]:
        """Get lengths for sequence of edges."""
        return [edge.length for edge in edges]


class NaturalFace:
    """Represents geometry and natural stress data of a single face.

    Parameters
    ----------
    mesh_xyz : ndarray of float
        XYZ vertex coordinates of the whole mesh as a (n, 3) array.
    vertices_ids : sequence of int
        Sequence of contiguous vertex indices.
    stress_goal : sequence of float
        Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field for the face,
        input over global directions and normalized over thickness.
        (default is None, setting a uniform stress field (1, 1, 0)).
    stress_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation.
    is_subface : boolean
        Whether the face is a tri subface of a quad face.

    Attributes
    ----------
    face_count : int
        The number of instantiated NaturalFaces.
    xyz : ndarray of float
        XYZ vertex coordinates of the face as a (n, 3) array.
    """

    face_count = 0

    def __new__(cls, mesh_xyz: VertexArray, vertices_ids: Sequence[int],
                stress_goal: Vec = None, stress_ref: Vec = None,
                is_subface: bool = False) -> None:
        v = len(vertices_ids)
        if v == 3:
            return super().__new__(TriFace)
        elif v == 4:
            return super().__new__(QuadFace)
        else:
            raise ValueError('Only tri and quad faces can be processed, '
                             f'A face with {v} vertices was input.')

    def __init__(self, mesh_xyz: VertexArray, vertices_ids: Sequence[int],
                 stress_goal: Vec = None, stress_ref: Vec = None,
                 is_subface: bool = False) -> None:
        self.cache = {}
        self._set_ids(vertices_ids, is_subface)
        self.xyz = mesh_xyz
        self.stress_ref = stress_ref
        self.stress_goal = stress_goal

    def update_xyz(self, mesh_xyz: VertexArray) -> None:
        """Update XYZ face coordinates and clear geometry cache."""
        self.cache.clear()
        self.xyz = mesh_xyz

    def _set_ids(self, vertices_ids: Sequence[int], is_subface: bool) -> None:
        self.vertices_ids = vertices_ids
        if is_subface:
            self.face_id = -1
        else:
            self.face_id = __class__.face_count
            __class__.face_count += 1

    def __len__(self) -> int:
        return len(self.vertices_ids)

    @property
    def xyz(self) -> VertexArray:
        """XYZ vertex coordinates of the face."""
        return self._xyz

    @xyz.setter
    def xyz(self, mesh_xyz: VertexArray) -> None:
        self._xyz = [mesh_xyz[v] for v in self.vertices_ids]

    @property
    @cache_iter
    def stress_goal(self) -> NpVec:
        """Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field for the face."""
        if self.stress_ref is None or is_isotropic(self._stress_goal):
            return self._stress_goal
        return self._calc_stress_goal()

    @stress_goal.setter
    def stress_goal(self, goal: Sequence[float]):
        self._stress_goal = asarray([1, 1, 0]) if goal is None else asarray(goal)
        if (not is_isotropic(self._stress_goal)) and (not self.stress_ref):
            raise ValueError("Non-isotropic stress state requires reference normal.")

    def _calc_stress_goal(self) -> Vec:
        """Calculate stress goal by intersection of the face with
        the plane defined by stress reference vector as its normal."""
        f = self.frame
        g = self._stress_goal
        x, z, ref = f.xaxis, f.zaxis, asarray(self.stress_ref)
        x_r = cross(z, ref)
        θ = atan2(cross(x, x_r).dot(z), x.dot(x_r))
        return transform_stress_angle(g, θ)

    def transform_stress_to_global(self, vec: NpVec) -> NpVec:
        """Transform stress pseudo-vector from local face frame to global frame."""
        R = asarray(Rotation.from_frame(self.frame))[:3, :3]
        return R.dot(append(vec, .0))

    @cache_iter
    def principal_stress(self, to_global: bool = False) -> Tuple[NDArray[(2,), float64], NDArray[(2, 2), float64]]:
        """Principal stress values and vectors from local stresses."""
        s = stress_vec_to_tensor(self.stress)
        eigenvals, eigenvecs = eig(s)
        # sort eigenvalues and corresponding vectors
        ids = argsort(-eigenvals)
        eigenvals, eigenvecs = eigenvals[ids], eigenvecs[ids, :]
        if to_global:
            eigenvecs = [self.transform_stress_to_global(v) for v in eigenvecs]
        return eigenvals, eigenvecs

    face_stresses = namedtuple('stresses', ['amplitudes', 'vectors'])

    @classmethod
    def get_stresses(cls, faces: Sequence[NaturalFace], stress_flag: int) -> NamedTuple:
        """Strategy for calculating stresses for a sequence of faces."""
        s = cls.face_stresses
        if stress_flag == -1:        # only tri (sub)face stresses
            return s(asarray(cls._get_tris_attr(faces, 'stress')), None)
        if stress_flag == 0:         # no stresses
            return s(None, None)
        if stress_flag == 1:         # stresses in local frames
            return s(asarray([f.stress for f in faces]), None)
        if (stress_flag in (2, 3)):  # principal stresses in local or global frame
            eigs = (f.principal_stress(to_global=(stress_flag == 3)) for f in faces)
            return s(*map(list, zip(*eigs)))
        raise ValueError("stress_flag parameter must be set to {0, 1, 2, 3}.")

    @classmethod
    def get_stress_goals(cls, faces: Sequence[NaturalFace]) -> NpVec:
        """Get stress goals for multiple tri (sub)faces. For quad faces,
        transformation into tri subface frames is hence not required."""
        return asarray(cls._get_tris_attr(faces, 'stress_goal'))

    @staticmethod
    def _get_tris_attr(faces: Sequence[NaturalFace], attr: Any) -> List:
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
    A quad face is composed of 4 pairwise overlapping tri faces.

    Parameters
    ----------
    mesh_xyz : ndarray of float
        XYZ vertex coordinates of the whole mesh as a (n, 3) array.
    vertices_ids : sequence of int
        Sequence of contiguous vertex indices.
    stress_goal : sequence of float
        Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field on the face,
        input over global directions and normalized over thickness.
        (default is None, setting a uniform stress field (1, 1, 0)).
    stress_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation.

    Attributes
    ----------
    frame : :class:`Frame`
        Local coordinate frame.
    rotations : generator of (2, 2) ndarrays of float
        Planarized rotation matrices from quad to tri subfaces.
    force_densities : list of float
        6 natural force densities of the edges.
    stress : ndarray of float
        Pseudo-vector of 2nd Piola-Kirchhoff stresses.
    """

    # vertex sequence of each the 4 tri subfaces of the quad face
    __TRI_VERTICES = ((1, 3, 0), (3, 1, 2), (2, 0, 1), (0, 2, 3))

    def __init__(self, mesh_xyz: VertexArray, vertices_ids: Sequence[int],
                 stress_goal: Vec = None, stress_ref: Vec = None) -> None:
        super().__init__(mesh_xyz, vertices_ids, stress_goal, stress_ref)
        self._set_tri_faces(mesh_xyz)

    def update_xyz(self, mesh_xyz: VertexArray) -> None:
        """Update XYZ face coordinates and clear geometry cache,
        both of quad face itself as of its composing tri subfaces."""
        super().update_xyz(mesh_xyz)
        for t in self.tri_faces:
            t.update_xyz(mesh_xyz)

    def _set_tri_faces(self, mesh_xyz: VertexArray) -> None:
        """Construct the 4 tri subfaces of the quad face."""
        tri_vertices_ids = (itemgetter(*self.__TRI_VERTICES[i])
                            (self.vertices_ids) for i in range(4))
        self.tri_faces = [TriFace(mesh_xyz, v_ids, self._stress_goal,
                          self.stress_ref, True) for v_ids in tri_vertices_ids]

    @property
    @cache_iter
    def area(self) -> float:
        """Face area, as half sum of composing tri subface areas."""
        return sum(t.area for t in self.tri_faces) / 2

    @property
    @cache_iter
    def frame(self) -> Frame:
        """Face frame, with origin at centroid and
        x-axis along midpoint of quad edge (1, 2)."""
        v0, v1, v2, v3 = self.xyz
        c0 = centroid_points(self.xyz)
        c1 = centroid_points((v1, v2))
        c2 = centroid_points((v2, v3))
        return Frame.from_points(c0, c1, c2)

    @property
    @cache_iter
    def rotations(self) -> Generator[NDArray[(2, 2), float64], None, None]:
        """Planar rotation matrices from quad face frame to
        each of the 4 tri subface frames."""
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
    def force_densities(self) -> NDArray[(6,), float64]:
        """6 natural force densities of the quad face for current
        geometry and goal 2nd Piola-Kirchhoff stresses."""
        na, nb, nc, nd = (t.force_densities for t in self.tri_faces)
        sum_force_densities = (na[1] + nc[0], nb[0] + nc[1], nb[1] + nd[0],
                               na[0] + nd[1], na[2] + nb[2], nc[2] + nd[2])
        return asarray([n / 2 for n in sum_force_densities])

    @property
    @cache_iter
    def stress(self) -> NpVec:
        """Pseudo-vector of 2nd Piola-Kirchhoff stresses at current geometry."""
        tot_a = self.area * 2
        tris_a = (t.area for t in self.tri_faces)
        tris_s = (t.stress for t in self.tri_faces)
        quad_s = self._transform_stress_tris_to_quad(tris_s)
        return sum(a * s for a, s in zip(tris_a, quad_s)) / tot_a

    def _transform_stress_tris_to_quad(self, tris_stress: NpVec
                                       ) -> Generator[NpVec, None, None]:
        """Transform stresses from tri subfaces frames to quad frame."""
        return (transform_stress(s, R) for s, R in zip(tris_stress, self.rotations))


class TriFace(NaturalFace):
    """Represents geometry and natural stress data of a single tri face.

    Parameters
    ----------
    mesh_xyz : ndarray of float
        XYZ vertex coordinates of the whole mesh as a (n, 3) array.
    vertices_ids : sequence of int
        Sequence of contiguous vertex indices.
    stress_goal : sequence of float
        Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field for the face,
        input over reference directions and normalized over thickness.
        (default is None, setting a uniform stress field (1, 1, 0)).
    stress_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation.

    Attributes
    ----------
    frame : :class:`Frame`
        Local coordinate frame.
    edge_lengths : tuple of float
        Ordered edge lengths.
    angles : tuple of float
        Angles in radians.
    area: float
        Face area.
    transformation : ndarray of float
        (3, 3) transformation matrix for tri face edges into stresses.
    transformation_inv : ndarray of float
        (3, 3) inverted transformation matrix for tri face stresses into edges.
    force_densities : list of float
        3 natural force densities of the edges.
    stress : ndarray of float
        Pseudo-vector of 2nd Piola-Kirchhoff stresses.
    """

    @property
    @cache_iter
    def frame(self) -> Frame:
        """Tri face frame, with origin at vertex 0 and x-axis along edge (0, 1)."""
        return Frame.from_points(*self.xyz)

    @property
    @cache_iter
    def edge_lengths(self) -> Tuple[float, float, float]:
        """Ordered edge lengths from euclidean distance between vertices."""
        ordered_xyz = self.xyz[1:] + self.xyz[:2]
        return tuple(euclidean_distance(u, v) for u, v in pairwise(ordered_xyz))

    @property
    @cache_iter
    def angles(self) -> Tuple[float, float, float]:
        """Angles in radians, calculated by law of cosines from edge lengths."""
        l0, l1, l2 = self.edge_lengths
        α = arc_cos((l0 ** 2 + l1 ** 2 - l2 ** 2) / (2 * l0 * l1))
        β = arc_cos((l1 ** 2 + l2 ** 2 - l0 ** 2) / (2 * l1 * l2))
        γ = pi - α - β
        return (α, β, γ)

    @property
    @cache_iter
    def area(self) -> float:
        """Face area."""
        l0, l1, l2 = self.edge_lengths
        return l1 * l2 * sin(self.angles[1]) / 2

    @property
    @cache_iter
    def transformation(self) -> NDArray[(3, 3), float64]:
        """3x3 transformation matrix for tri face edge directions
        into stresses in local frame. Its column vectors are unit
        edge stresses described in the local face frame."""
        α, β, γ = self.angles
        T = [[c2(γ),                c2(β),   1],  # noqa
             [s2(γ),                s2(β),   0],  # noqa
             [s(γ) * c(γ),   -s(β) * c(β),   0]]  # noqa
        return asarray(T)

    @property
    @check_singularity
    def transformation_inv(self) -> NpVec:
        """3x3 transformation matrix for tri face stresses
        in local frame into edge directions."""
        return inv(self.transformation)

    @property
    def force_densities(self) -> NpVec:
        """3 natural force densities of the tri face for current
        geometry and goal (2nd Piola-Kirchhoff) stresses."""
        a = self.area
        g = self.stress_goal
        Li2 = asarray([1 / (ln ** 2) for ln in self.edge_lengths])
        Ti = self.transformation_inv
        self._force_densities = a * Li2 * Ti.dot(g)
        return self._force_densities

    @property
    @cache_iter
    def stress(self) -> NpVec:
        """Pseudo-vector of 2nd Piola-Kirchhoff stresses at current geometry."""
        L2 = asarray([ln ** 2 for ln in self.edge_lengths])
        a = self.area
        T = self.transformation
        # force densities of previous geometry
        n = self._force_densities
        stress = (T * L2).dot(n) / a
        return stress


# =================================================
# mesh data processing
# =================================================

def mesh_preprocess(mesh: Mesh, goals: Goals) -> Tuple[
        VertexArray, List[NaturalEdge], List[NaturalFace]]:
    """Pre-process mesh to lists of elements.

    Parameters
    ----------
    mesh : :class:`Mesh`
        Instance of Mesh datastructure.
    goals: :class:'Goals'
        Instance of Goals class.

    Returns
    ----------
    list of NaturalFace
        Processed mesh faces.
    list of NaturalEdge
        Processed mesh edges.
    ndarray of float
        XYZ vertex coordinates of the whole mesh as a (n, 3) array.
    """
    # vertex indices mapping
    v_index = mesh.key_index()
    mesh_xyz = [mesh.vertex_coordinates(v) for v in mesh.vertices()]
    edges_vts = ([v_index[u], v_index[v]] for u, v in mesh.edges())
    faces_vts = ([v_index[w] for w in mesh.face_vertices(f)]
                 for f in mesh.faces())

    # set natural faces and edges
    faces = [NaturalFace(mesh_xyz, face_v, sp, goals.stress_ref)
             for face_v, sp in zip(faces_vts, goals.stress)]
    edges = [e for e in [NaturalEdge(mesh_xyz, edge_v, fp, qp) for edge_v, fp, qp
             in zip(edges_vts, goals.forces, goals.force_densities)] if e]

    return asarray(mesh_xyz), edges, faces
