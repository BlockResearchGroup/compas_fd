from numpy import add
from numpy import array
from numpy import asarray
from numpy import average
from numpy import cross
from numpy import empty
from numpy import float64
from numpy import roll

from numpy.linalg import norm
from scipy.sparse import coo_matrix

from compas.datastructures import Mesh

from typing import Any
from typing import List
from typing import Sequence
from typing import Union
from typing_extensions import Annotated
from nptyping import NDArray


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
    LM : ndarray of float
        global vertex load matrix as (v x 3) array.
    FN : ndarray of float
        Face normals for current geometry as (f x 3) array.
    TA : ndarray of float
        Tributary areas matrix as sparse (v x f) array.
        Entry a_ij holds tributary area of face j for vertex i.

    Examples
    --------
    >>> import compas
    >>> from compas.datastructures import Mesh
    >>> from compas_fd import LoadCalculator
    >>> mesh = Mesh.from_obj(compas.get('hypar.obj'))
    >>> dva = {'px': .0, 'py': .0, 'pz': .1}
    >>> dfa = {'t': .1, 'is_loaded': True, 'wind': 1.0}
    >>> mesh.attributes.update({'density': 22.0})
    >>> mesh.update_default_vertex_attributes(dva)
    >>> mesh.update_default_face_attributes(dfa)
    >>> lc = LoadCalculator(mesh)
    >>> xyz = [mesh.vertex_coordinates(v)
               for v in mesh.vertices()]
    >>> load_mat = lc(xyz)
    >>> lc.update_mesh()
    """

    # attribute names in mesh data
    PX, PY, PZ = 'px', 'py', 'pz'           # input vertex loads
    _PX, _PY, _PZ = '_px', '_py', '_pz'     # resultant vertex loads
    RHO = 'density'
    THICKNESS = 't'
    HAS_SW = 'is_loaded'
    NORMAL = 'wind'
    PROJECT = 'snow'

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
        if not self._load_flags['any_face_load'] and not process_all_faces:
            return self._vertex_loads
        self.LM = array(self._vertex_loads, copy=True)
        self._process_faces(asarray(xyz).reshape(-1, 3), process_all_faces)
        self._add_face_loads()
        return self.LM

    def update_mesh(self) -> None:
        """Set the resultant vertex loads in mesh data by
        using the latest calculated internal load matrix."""
        try:
            LM = self.LM
        except AttributeError:
            LM = self._vertex_loads
        for v, vkey in enumerate(self.mesh.vertices()):
            self.mesh.vertex_attributes(vkey, [self._PX, self._PY, self._PZ],
                                        [LM[v, 0], LM[v, 1], LM[v, 2]])

    def _set_mesh_maps(self) -> None:
        """Set mesh counts and maps."""
        self._v_count = self.mesh.number_of_vertices()
        self._f_count = self.mesh.number_of_faces()
        self._v_id = self.mesh.key_index()
        self.FN = None
        self.TA = None

    def _preprocess_loads(self) -> None:
        """Preprocess loads into arrays."""
        self._vertex_loads = asarray(self.mesh.vertices_attributes(
                                     names=(self.PX, self.PY, self.PZ))
                                     ).reshape((self._v_count, 3))
        rho = self.mesh.attributes[self.RHO]
        self._weight = asarray([-t * w * rho for t, w in
                                self.mesh.faces_attributes([self.THICKNESS, self.HAS_SW])]
                               ).reshape((self._f_count, 1))
        self._normal_loads = asarray(self.mesh.faces_attribute(self.NORMAL)
                                     ).reshape((self._f_count, 1))
        self._project_loads = asarray(self.mesh.faces_attribute(self.PROJECT)
                                      ).reshape((self._f_count, 1))

    def _set_load_flags(self) -> None:
        """Set flags for which load types are applied."""
        bool_weight = array(self._weight, dtype=bool)
        bool_normal = array(self._normal_loads, dtype=bool)
        bool_project = array(self._project_loads, dtype=bool)
        self._oriented_loads = bool_normal + bool_project
        self._face_loads = self._oriented_loads + bool_weight
        self._load_flags = {'any_face_load': self._face_loads.any(),
                            'any_weight': bool_weight.any(),
                            'any_normal': bool_normal.any(),
                            'any_projected': bool_project.any()}

    def _add_face_loads(self) -> None:
        """Add active face loads to the global load matrix."""
        if self._load_flags['any_weight']:
            self._add_weight()
        if self._load_flags['any_normal']:
            self._add_normal_loads()
        if self._load_flags['any_projected']:
            self._add_projected_loads()

    def _process_faces(self, xyz: NDArray[(Any, 3), float64],
                       process_all_faces: bool) -> None:
        """Calculate normals and tributary areas per face,
        for the vertex coordinates of the current geometry."""
        self.FN = empty((self._f_count, 3), dtype=float)
        trib_data = []; trib_rows = []; trib_cols = []  # noqa

        for f, fkey in enumerate(self.mesh.faces()):
            if not (self._face_loads[f] or process_all_faces):
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
            if self._oriented_loads[f] or process_all_faces:
                self.FN[f, :] = add.reduce(cps)

        self.FN /= norm(self.FN, axis=1)[:, None]
        self.TA = coo_matrix((trib_data, (trib_rows, trib_cols)),
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
        and add them into the global load matrix."""
        self.LM[:, 2:] += self.TA.dot(self._weight)

    def _add_normal_loads(self) -> None:
        """Convert all normal face loads into global vertex loads
        and add them into the global load matrix."""
        NL = self.FN * self._normal_loads
        self.LM += self.TA.dot(NL)

    def _add_projected_loads(self) -> None:
        """Convert all Z-projected face loads into global vertex loads
        and add them into the global load matrix."""
        z = asarray([0, 0, -1]).reshape((3, 1))
        PL = self.FN.dot(z) * self._project_loads
        self.LM[:, 2:] += self.TA.dot(PL)
