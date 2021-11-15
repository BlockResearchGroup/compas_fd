from typing import Any
from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Annotated
from nptyping import NDArray

from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import diags
from scipy.sparse import vstack as svstack

from compas.datastructures import Mesh
from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_fd.result import Result
from .numerical_data import NumericalData
from .numerical_data import lazy_eval
from .face_data import FaceDataMixin


class FDNumericalData(FaceDataMixin, NumericalData):
    """Stores numerical data used by the force density algorithms."""

    def __init__(self,
                 vertices: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
                 fixed: List[int],
                 edges: List[Tuple[int, int]],
                 force_densities: List[float],
                 loads: Optional[Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]] = None
                 ):
        self.xyz = vertices
        self.fixed = fixed
        self.edges = edges
        self.force_densities = force_densities
        self.loads = loads

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
    def xyz(self) -> NDArray[(Any, 3), float64]:
        return self._xyz

    @xyz.setter
    def xyz(self, vertices) -> None:
        self._xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        self.reset_xyz()

    def reset_xyz(self) -> None:
        self._lengths = None
        self._residuals = None
        self._coordinate_difference_matrices = None
        self._equilibrium_matrix = None
        if getattr(self, 'has_face_data', False):
            FaceDataMixin.reset_face_data(self)

    @property
    def fixed(self) -> List[int]:
        return self._fixed

    @fixed.setter
    def fixed(self, fixed) -> None:
        self._fixed = fixed
        self._free = list(set(range(len(self.xyz))) - set(fixed))

    @property
    def free(self) -> List[int]:
        return self._free

    @property
    def edges(self) -> List[Tuple[int, int]]:
        return self._edges

    @edges.setter
    def edges(self, edges: List[List[int]]) -> None:
        self._edges = edges
        self._connectivity_matrix = None
        self._connectivity_matrix_free = None
        self._connectivity_matrix_fixed = None

    @property
    @lazy_eval
    def connectivity_matrix(self) -> NDArray[(Any, Any), float64]:
        return connectivity_matrix(self.edges, 'csr')

    @property
    @lazy_eval
    def connectivity_matrix_free(self) -> NDArray[(Any, Any), float64]:
        return self.connectivity_matrix[:, self.free]

    @property
    @lazy_eval
    def connectivity_matrix_fixed(self) -> NDArray[(Any, Any), float64]:
        return self.connectivity_matrix[:, self.fixed]

    @property
    @lazy_eval
    def coordinate_difference_matrices(self) -> Tuple[NDArray[(Any, Any), float64]]:
        uvw = self.C.dot(self.xyz)
        U = diags([uvw[:, 0].flatten()], [0])
        V = diags([uvw[:, 1].flatten()], [0])
        W = diags([uvw[:, 2].flatten()], [0])
        return (U, V, W)

    @property
    @lazy_eval
    def equilibrium_matrix(self) -> NDArray[(Any, Any), float64]:
        U, V, W = self.coordinate_difference_matrices
        return svstack((self.C.T.dot(U), self.C.T.dot(V), self.C.T.dot(W)))

    @property
    def force_densities(self) -> NDArray[(Any, 1), float64]:
        return self._force_densities

    @force_densities.setter
    def force_densities(self,
                        force_densities: Union[List[float], NDArray[(Any, 3), float64]]
                        ) -> None:
        self._force_densities = asarray(force_densities, dtype=float64).reshape((-1, 1))
        self._force_densities_matrix = None
        self._stifness_matrix = None
        self._stifness_matrix_free = None
        self._stifness_matrix_fixed = None
        self._forces = None
        self._residuals = None

    @property
    @lazy_eval
    def force_densities_matrix(self) -> NDArray[(Any, Any), float64]:
        return diags([self.force_densities.flatten()], [0])

    @property
    def loads(self) -> NDArray[(Any, 3), float64]:
        return self._loads

    @loads.setter
    def loads(self,
              loads: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]]
              ) -> None:
        self._loads = (zeros_like(self.xyz) if loads is None else
                       asarray(loads, dtype=float64).reshape((-1, 3)))
        self._residuals = None

    @property
    @lazy_eval
    def stifness_matrix(self) -> NDArray[(Any, Any), float64]:
        return self.C.T.dot(self.Q).dot(self.C)

    @property
    @lazy_eval
    def stifness_matrix_free(self) -> NDArray[(Any, Any), float64]:
        return self.Ci.T.dot(self.Q).dot(self.Ci)

    @property
    @lazy_eval
    def stifness_matrix_fixed(self) -> NDArray[(Any, Any), float64]:
        return self.Ci.T.dot(self.Q).dot(self.Cf)

    @property
    @lazy_eval
    def forces(self) -> NDArray[(Any, 1), float64]:
        return self.q * self.ls

    @property
    @lazy_eval
    def lengths(self) -> NDArray[(Any, 1), float64]:
        return normrow(self.C.dot(self.xyz))

    @property
    @lazy_eval
    def residuals(self) -> NDArray[(Any, 3), float64]:
        return self.p - self.D.dot(self.xyz)

    # aliases
    C = connectivity_matrix
    Ci = connectivity_matrix_free
    Cf = connectivity_matrix_fixed
    UVW = coordinate_difference_matrices
    E = equilibrium_matrix
    q = force_densities
    Q = force_densities_matrix
    p = loads
    D = stifness_matrix
    Di = stifness_matrix_free
    Df = stifness_matrix_fixed
    f = forces
    ls = lengths
    r = residuals
