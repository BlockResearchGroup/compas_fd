from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from dataclasses import dataclass

from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import diags

from compas.datastructures import Mesh
from compas.numerical import connectivity_matrix

from .numerical_data import NumericalData
from .face_data import FaceDataMixin


class FDNumericalData(FaceDataMixin, NumericalData):
    """Stores numerical data used by the force density algorithms."""
    free: int
    fixed: int
    xyz: NDArray[(Any, 3), float64]
    C: NDArray[(Any, Any), int]
    q: NDArray[(Any, 1), float64]
    Q: NDArray[(Any, Any), float64]
    p: NDArray[(Any, 1), float64]
    A: NDArray[(Any, Any), float64]
    Ai: NDArray[(Any, Any), float64]
    Af: NDArray[(Any, Any), float64]
    forces: NDArray[(Any, 1), float64] = None
    lengths: NDArray[(Any, 1), float64] = None
    residuals: NDArray[(Any, 3), float64] = None
    tangent_residuals: NDArray[(Any, 3), float64] = None
    normal_residuals: NDArray[(Any, 1), float64] = None

    @classmethod
    def from_params(cls,
                    vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
                    fixed: List[int],
                    edges: List[Tuple[int, int]],
                    forcedensities: List[float],
                    loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None
                    ):
        """Construct numerical arrays from force density solver input parameters."""
        free = list(set(range(len(vertices))) - set(fixed))
        xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        C = connectivity_matrix(edges, 'csr')
        Ci = C[:, free]
        Cf = C[:, fixed]
        q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
        Q = diags([q.flatten()], [0])
        p = (zeros_like(xyz) if loads is None else
             asarray(loads, dtype=float64).reshape((-1, 3)))
        A = C.T.dot(Q).dot(C)
        Ai = Ci.T.dot(Q).dot(Ci)
        Af = Ci.T.dot(Q).dot(Cf)
        return cls(free, fixed, xyz, C, q, Q, p, A, Ai, Af)

    @classmethod
    def from_mesh(cls, mesh: Mesh):
        """Construct numerical arrays from input mesh."""
        v_i = mesh.vertex_index()
        vertices = asarray(mesh.vertices_attributes('xyz'))
        fixed = [v_i[v] for v in mesh.vertices_where({'is_anchor': True})]
        edges = [(v_i[u], v_i[v]) for u, v in mesh.edges_where({'_is_edge': True})]
        force_densities = asarray([attr['q'] for key, attr in
                                   mesh.edges_where({'_is_edge': True}, True)])
        loads = asarray(mesh.vertices_attributes(('px', 'py', 'pz')))

        numdata = cls(vertices, fixed, edges, force_densities, loads)
        super(FDNumericalData, numdata).__init__(mesh)
        numdata.has_face_data = True
        return numdata

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        return Result(self.xyz, self.residuals, self.forces, self.lengths)

    @property
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, vertices):
        self._xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        self.reset_xyz()

    def reset_xyz(self):
        self._lengths = None
        self._residuals = None
        if getattr(self, 'has_face_data', False):
            FaceDataMixin.reset_face_data(self)

    @property
    def fixed(self):
        return self._fixed

    @fixed.setter
    def fixed(self, fixed):
        self._fixed = fixed
        self._free = list(set(range(len(self.xyz))) - set(fixed))

    @property
    def free(self):
        return self._free

    @property
    def edges(self):
        return self._edges

    @edges.setter
    def edges(self, edges):
        self._edges = edges
        self._connectivity_matrix = None
        self._connectivity_matrix_free = None
        self._connectivity_matrix_fixed = None

    @property
    def connectivity_matrix(self):
        if self._connectivity_matrix is None:
            self._connectivity_matrix = connectivity_matrix(self.edges, 'csr')
        return self._connectivity_matrix

    @property
    def connectivity_matrix_free(self):
        if self._connectivity_matrix_free is None:
            self._connectivity_matrix_free = self.connectivity_matrix[:, self.free]
        return self._connectivity_matrix_free

    @property
    def connectivity_matrix_fixed(self):
        if self._connectivity_matrix_fixed is None:
            self._connectivity_matrix_fixed = self.connectivity_matrix[:, self.fixed]
        return self._connectivity_matrix_fixed

    @property
    def force_densities(self):
        return self._force_densities

    @force_densities.setter
    def force_densities(self, force_densities):
        self._force_densities = asarray(force_densities, dtype=float64).reshape((-1, 1))
        self._force_densities_matrix = None
        self._stifness_matrix = None
        self._stifness_matrix_free = None
        self._stifness_matrix_fixed = None
        self._forces = None
        self._residuals = None

    @property
    def force_densities_matrix(self):
        if self._force_densities_matrix is None:
            self._force_densities_matrix = diags(
                [self.force_densities.flatten()], [0])
        return self._force_densities_matrix

    @property
    def loads(self):
        return self._loads

    @loads.setter
    def loads(self, loads):
        self._loads = (zeros_like(self.xyz) if loads is None else
                       asarray(loads, dtype=float64).reshape((-1, 3)))
        self._residuals = None

    @property
    def stifness_matrix(self):
        if self._stifness_matrix is None:
            self._stifness_matrix = self.C.T.dot(self.Q).dot(self.C)
        return self._stifness_matrix

    @property
    def stifness_matrix_free(self):
        if self._stifness_matrix_free is None:
            self._stifness_matrix_free = self.Ci.T.dot(self.Q).dot(self.Ci)
        return self._stifness_matrix_free

    @property
    def stifness_matrix_fixed(self):
        if self._stifness_matrix_fixed is None:
            self._stifness_matrix_fixed = self.Ci.T.dot(self.Q).dot(self.Cf)
        return self._stifness_matrix_fixed

    @property
    def forces(self):
        if self._forces is None:
            self._forces = self.q * self.ls
        return self._forces

    @property
    def lengths(self):
        if self._lengths is None:
            self._lengths = normrow(self.C.dot(self.xyz))
        return self._lengths

    @property
    def residuals(self):
        if self._residuals is None:
            self._residuals = self.p - self.D.dot(self.xyz)
        return self._residuals

    # aliases
    C = connectivity_matrix
    Ci = connectivity_matrix_free
    Cf = connectivity_matrix_fixed
    q = force_densities
    Q = force_densities_matrix
    p = loads
    D = stifness_matrix
    Di = stifness_matrix_free
    Df = stifness_matrix_fixed
    f = forces
    ls = lengths
    r = residuals
