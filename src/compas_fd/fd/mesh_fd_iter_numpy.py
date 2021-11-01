from typing import Sequence

from numpy import array
from numpy import float64
from numpy.linalg import norm

import compas_fd
# from compas_fd.loads import LoadCalculator
from compas_fd.constraints import Constraint
from .fd_numpy import fd_numpy


# /for LoadCalculator ----
from numpy import add
from numpy import asarray
from numpy import average
from numpy import cross
from numpy import roll
from numpy import zeros

from scipy.sparse import coo_matrix

from compas.datastructures import Mesh

from typing import Any
from typing import List
from typing import Union
from typing_extensions import Annotated
from nptyping import NDArray
# \for LoadCalculator ----


def mesh_fd_iter_numpy(mesh: 'compas_fd.datastructures.CableMesh',
                       constraints: Sequence[Constraint] = None,
                       max_iter: int = 30,
                       tolerance: float = 1E-3
                       ) -> 'compas_fd.datastructures.CableMesh':
    """Iteratively find the equilibrium shape of a mesh for the given force densities.

    Parameters
    ----------
    mesh : :class:`compas_fd.datastructures.CableMesh`
        The mesh to equilibriate.
    constraints: sequence
        Sequence of vertex constraints.
    max_iter: int
        The maximum number of iterations.
    tolerance: float
        Tolerance for maximum vertex coordinate
        distances between consecutive iterations.

    Returns
    -------
    :class:`compas_fd.datastructures.CableMesh`
        The function updates the mesh in place,
        but returns a reference to the updated mesh as well
        for compatibility with RPCs.

    """
    k_i = mesh.key_index()
    fixed = [k_i[key] for key in mesh.vertices_where({'is_anchor': True})]
    xyz = array(mesh.vertices_attributes('xyz'), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in mesh.edges_where({'_is_edge': True})]
    q = array([attr['q'] for key, attr in mesh.edges_where({'_is_edge': True}, True)],
              dtype=float64).reshape((-1, 1))
    loads = LoadCalculator(mesh)

    for k in range(max_iter):
        p = loads(xyz)
        result = fd_numpy(vertices=xyz, fixed=fixed, edges=edges, forcedensities=q, loads=p)
        _xyz = Constraint.update_vertices(result, constraints)
        if norm(_xyz - xyz).max() < tolerance:
            break
        xyz = _xyz

    print("Convergence reached at iteration {}".format(k))
    result_update_mesh(result, mesh)
    loads.update_mesh()
    return mesh


# to be replaced by a bound method in result class
def result_update_mesh(result, mesh):
    """Update mesh with solver results."""
    k_i = mesh.key_index()
    for key, attr in mesh.vertices(True):
        index = k_i[key]
        attr['x'] = result.vertices[index, 0]
        attr['y'] = result.vertices[index, 1]
        attr['z'] = result.vertices[index, 2]
        attr['_rx'] = result.residuals[index, 0]
        attr['_ry'] = result.residuals[index, 1]
        attr['_rz'] = result.residuals[index, 2]

    for index, (key, attr) in enumerate(mesh.edges_where({'_is_edge': True}, True)):
        attr['_f'] = result.forces[index, 0]
        attr['_l'] = result.lenghts[index, 0]


class LoadCalculator:
    """Represents assembly of all input loads into a global vertex load matrix.

    By calling an instance of LoadCalculator with vertex coordinates,
    the global load matrix is calculated for the current geometry.
    This calculation is lazy, face data (tributary areas or normals)
    is only calculated if face loads or oriented loads are applied.

    Parameters
    ----------
    mesh : :class:`Mesh`
        Instance of Mesh datastructure.

    Attributes
    ----------
    RL : ndarray of float
        global resultant vertex load matrix as (v x 3) array.
    TA : ndarray of float
        Tributary areas matrix as sparse (v x f) array.
        Entry a_ij holds tributary area of face j for vertex i.
    FN : ndarray of float
        Face normals for current geometry as (f x 3) array.

    Examples
    --------
    >>> import compas
    >>> from compas.datastructures import Mesh
    >>> from compas_fd import LoadCalculator
    >>> mesh = Mesh.from_obj(compas.get('hypar.obj'))
    >>> ma = {'density': 24.0, 'point_lc': 1, 'weight_lc': 1,
              'wind_lc': 1, 'snow_lc': 1}
    >>> dva = {'px': .0, 'py': .0, 'pz': -.1, 't': .1}
    >>> dfa = {'wind': 1.0, 'snow': .0, 'has_weight': True,
               'has_wind': True, 'has_snow': False}
    >>> mesh.attributes.update(ma)
    >>> mesh.update_default_vertex_attributes(dva)
    >>> mesh.update_default_face_attributes(dfa)
    >>> lc = LoadCalculator(mesh)
    >>> xyz = [mesh.vertex_coordinates(v)
               for v in mesh.vertices()]
    >>> load_mat = lc(xyz)
    >>> lc.update_mesh()
    """

    # hardcoded attribute names in mesh data map
    PX, PY, PZ = 'px', 'py', 'pz'           # input vertex loads
    _PX, _PY, _PZ = '_px', '_py', '_pz'     # resultant vertex loads

    RHO = 'density'
    VTS_LC = 'point_lc'
    WEIGHT_LC = 'weight_lc'
    NORMAL_LC = 'wind_lc'
    PROJ_LC = 'snow_lc'

    TH = 't'
    NORMAL = 'wind'
    PROJECT = 'snow'
    HAS_SW = 'has_weight'
    HAS_NORMAL = 'has_wind'
    HAS_PROJ = 'has_snow'

    def __init__(self, mesh: Mesh) -> None:
        self.mesh = mesh
        self._set_mesh_maps()
        self._preprocess_loads()
        self._set_load_flags()

    def __call__(self, xyz: Union[Sequence[Annotated[List[float], 3]], NDArray[(Any, 3), float64]],
                 process_all_faces: bool = False) -> NDArray[(Any, 3), float64]:
        """Assemble global load matrix for current geometry.

        Parameters
        ----------
        xyz : ndarray of float  or  list of lists
            Coordinates of the vertices as (v x 3) array.
        process_all_faces : bool
            Switch to calculate all face tributary areas
            and normals, regardless of the applied loads.
            Default is ``False``.

        Returns
        -------
        ndarray of float
            Resultant global vertex loads as (v x 3) array.
        """
        if not self._any_face_load and not process_all_faces:
            return self._vertex_loads
        self._RL = array(self._vertex_loads, copy=True)
        self._process_faces(asarray(xyz).reshape(-1, 3), process_all_faces)
        self._add_face_loads()
        return self._RL

    def update_mesh(self) -> None:
        """Set the resultant vertex loads in the mesh data map by
        using the latest calculated internal load matrix."""
        RL = self.RL
        for v, vkey in enumerate(self.mesh.vertices()):
            self.mesh.vertex_attributes(vkey, [self._PX, self._PY, self._PZ],
                                        [RL[v, 0], RL[v, 1], RL[v, 2]])

    @property
    def RL(self):
        """global resultant vertex load matrix as (v x 3) array."""
        return getattr(self, '_RL', self._vertex_loads)

    @property
    def TA(self):
        """Tributary areas matrix as sparse (v x f) array.
        Entry a_ij holds tributary area of face j for vertex i."""
        return getattr(self, '_TA', zeros((self._v_count, self._f_count)))

    @property
    def FN(self):
        """Face normals for current geometry as (f x 3) array."""
        return getattr(self, '_FN', zeros((self._f_count, 3)))

    def _set_mesh_maps(self) -> None:
        """Set mesh counts and maps."""
        self._v_count = self.mesh.number_of_vertices()
        self._f_count = self.mesh.number_of_faces()
        self._v_id = self.mesh.key_index()

    def _preprocess_loads(self) -> None:
        """Preprocess loads into arrays."""
        vts_lc, weight_lc, normal_lc, proj_lc, rho = (self.mesh.attributes[key] for key in (
            self.VTS_LC, self.WEIGHT_LC, self.NORMAL_LC, self.PROJ_LC, self.RHO))

        self._vertex_loads = asarray(self.mesh.vertices_attributes(
                                     names=(self.PX, self.PY, self.PZ))
                                     ).reshape((self._v_count, 3)) * vts_lc
        self._v_weights = asarray(self.mesh.vertices_attribute(self.TH)) * rho * weight_lc
        self._normal_loads = asarray([n * hn for n, hn in self.mesh.faces_attributes(
                                     [self.NORMAL, self.HAS_NORMAL])]
                                     ).reshape((self._f_count, 1)) * normal_lc
        self._project_loads = asarray([p * hp for p, hp in self.mesh.faces_attributes(
                                      [self.PROJECT, self.HAS_PROJ])]
                                      ).reshape((self._f_count, 1)) * proj_lc

    def _set_load_flags(self) -> None:
        """Set flags for which face load types are applied."""
        have_normal = array(self._normal_loads, dtype=bool)
        have_projected = array(self._project_loads, dtype=bool)
        self._have_weight = array(self.mesh.faces_attribute(self.HAS_SW),
                                  dtype=bool).reshape((self._f_count, 1))
        self._have_oriented_load = have_normal + have_projected
        self._have_face_load = self._have_oriented_load + self._have_weight
        self._any_face_load = self._have_face_load.any()
        self._any_weight = self._have_weight.any()
        self._any_normal = have_normal.any()
        self._any_projected = have_projected.any()

    def _add_face_loads(self) -> None:
        """Add active face loads to the global load matrix."""
        if self._any_weight:
            self._add_weight()
        if self._any_normal:
            self._add_normal_loads()
        if self._any_projected:
            self._add_projected_loads()

    def _process_faces(self, xyz: NDArray[(Any, 3), float64],
                       process_all_faces: bool) -> None:
        """Calculate normals and tributary areas per face,
        for the vertex coordinates of the current geometry."""
        self._FN = zeros((self._f_count, 3), dtype=float)
        trib_data = []; trib_rows = []; trib_cols = []  # noqa

        for f, fkey in enumerate(self.mesh.faces()):
            if not (self._have_face_load[f] or process_all_faces):
                continue
            vts = [self._v_id[v] for v in
                   self.mesh.face_vertices(fkey)]
            f_xyz = xyz[vts, :]
            cps = self._face_cross_products(f_xyz)
            # face tributary areas per vertex
            part_areas = 0.25 * norm(cps, axis=1)
            trib_data.extend(part_areas + roll(part_areas, -1))
            trib_rows.extend(vts)
            trib_cols.extend([f] * len(vts))
            # face normal vector
            if self._have_oriented_load[f] or process_all_faces:
                self._FN[f, :] = add.reduce(cps)

        self._FN /= norm(self._FN, axis=1)[:, None]
        self._TA = coo_matrix((trib_data, (trib_rows, trib_cols)),
                              (self._v_count, self._f_count)).tocsr()

    def _face_cross_products(self, f_xyz: NDArray[(Any, 3), float64]
                             ) -> NDArray[(Any, 3), float64]:
        """Utility to calculate cross products of the consecutive
        (centroid -> vertex) vectors for each of the vertices of the face."""
        centroid = average(f_xyz, axis=0)
        v = f_xyz - centroid
        vr = roll(v, -1, axis=0)
        return cross(v, vr)

    def _add_weight(self) -> None:
        """Convert all face self-weights into global vertex loads
        and add them into the global load matrix.
        Loads are stepped per vertex tributary area."""
        self._RL[:, 2:] -= (self._v_weights * add.reduce(
                            self._TA * self._have_weight, axis=1)
                            ).reshape((-1, 1))

    def _add_normal_loads(self) -> None:
        """Convert all normal face loads into global vertex loads
        and add them into the global load matrix."""
        NL = self._FN * self._normal_loads
        self._RL += self._TA.dot(NL)

    def _add_projected_loads(self) -> None:
        """Convert all Z-projected face loads into global vertex loads
        and add them into the global load matrix."""
        z = asarray([0, 0, -1]).reshape((3, 1))
        PL = self._FN.dot(z) * self._project_loads
        self._RL[:, 2:] += self._TA.dot(PL)
