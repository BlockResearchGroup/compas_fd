from dataclasses import astuple
from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Tuple

from compas.datastructures import Mesh
from compas.matrices import connectivity_matrix
from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import diags

from compas_fd.types import FloatNx1
from compas_fd.types import FloatNx3
from compas_fd.types import FloatNxM
from compas_fd.types import IntNx2
from compas_fd.types import IntNxM

from .result import Result


@dataclass
class FDNumericalData:
    """Data Class for for storing numerical data used by the force density algorithms."""

    free: int
    fixed: int
    xyz: FloatNx3
    edges: IntNx2
    C: IntNxM
    q: FloatNx1
    Q: FloatNxM
    p: FloatNx3
    A: FloatNxM
    Ai: FloatNxM
    Af: FloatNxM
    forces: Optional[FloatNx1] = None
    lengths: Optional[FloatNx1] = None
    residuals: Optional[FloatNx3] = None
    tangent_residuals: Optional[FloatNx3] = None
    normal_residuals: Optional[FloatNx3] = None

    def __iter__(self):
        return iter(astuple(self))

    @classmethod
    def from_params(
        cls,
        vertices: FloatNx3,
        fixed: List[int],
        edges: List[Tuple[int, int]],
        forcedensities: List[float],
        loads: Optional[FloatNx3] = None,
    ) -> "FDNumericalData":
        """Construct numerical arrays from force density solver input parameters.

        Parameters
        ----------
        vertices : FloatNx3
        fixed : list[int]
        edges : list[tuple[int, int]]
        forcedensities : list[float]
        loads : FloatNx3, optional

        Returns
        -------
        FDNumericalData

        """
        free = list(set(range(len(vertices))) - set(fixed))
        xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        C = connectivity_matrix(edges, "csr")
        Ci = C[:, free]
        Cf = C[:, fixed]
        q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
        Q = diags([q.flatten()], [0])
        p = zeros_like(xyz) if loads is None else asarray(loads, dtype=float64).reshape((-1, 3))
        A = C.T.dot(Q).dot(C)
        Ai = Ci.T.dot(Q).dot(Ci)
        Af = Ci.T.dot(Q).dot(Cf)
        return cls(free, fixed, xyz, edges, C, q, Q, p, A, Ai, Af)

    @classmethod
    def from_mesh(cls, mesh: Mesh) -> "FDNumericalData":
        """Construct numerical arrays from input mesh.

        Parameters
        ----------
        mesh : :class:`compas.datastructures.Mesh`

        Returns
        -------
        FDNumericalData

        """
        raise NotImplementedError

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        return Result(self.xyz, self.residuals, self.forces, self.lengths)

    def update_forcedensities(self, edges, newqs):
        """Update the force densities and update the associated matrices.

        Parameters
        ----------
        edges : list[int]
            A list of indices in the force density array.
        newqs : list[float]
            The new force densities corresponding to the edge indices.

        Returns
        -------
        None

        """
        C = self.C
        Ci = C[:, self.free]
        Cf = C[:, self.fixed]
        self.q[edges] = newqs
        self.Q = diags([self.q.flatten()], [0])
        self.A = C.T.dot(self.Q).dot(C)
        self.Ai = Ci.T.dot(self.Q).dot(Ci)
        self.Af = Ci.T.dot(self.Q).dot(Cf)
