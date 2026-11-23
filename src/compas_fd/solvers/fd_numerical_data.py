from collections.abc import Iterator
from collections.abc import Sequence
from dataclasses import astuple
from dataclasses import dataclass
from typing import cast

from compas.datastructures import Mesh
from compas.linalg import connectivity_matrix
from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import csc_matrix
from scipy.sparse import csr_matrix
from scipy.sparse import dia_matrix

from compas_fd._scipy import diagonal
from compas_fd._scipy import weighted_product
from compas_fd.types import FloatArray
from compas_fd.types import FloatNx3

from .result import Result


@dataclass
class FDNumericalData:
    """Data Class for for storing numerical data used by the force density algorithms."""

    free: list[int]
    fixed: list[int]
    xyz: FloatArray
    edges: Sequence[tuple[int, int]]
    C: csr_matrix
    q: FloatArray
    Q: dia_matrix
    p: FloatArray
    A: csc_matrix
    Ai: csc_matrix
    Af: csc_matrix
    forces: FloatArray | None = None
    lengths: FloatArray | None = None
    residuals: FloatArray | None = None
    tangent_residuals: FloatArray | None = None
    normal_residuals: FloatArray | None = None

    def __iter__(self) -> Iterator[object]:
        return iter(astuple(self))

    @classmethod
    def from_params(
        cls,
        vertices: FloatNx3,
        fixed: list[int],
        edges: Sequence[tuple[int, int]],
        forcedensities: Sequence[float],
        loads: FloatNx3 | None = None,
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
        Ci = cast(csr_matrix, C[:, free])
        Cf = cast(csr_matrix, C[:, fixed])
        q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
        Q = diagonal(q)
        p = zeros_like(xyz) if loads is None else asarray(loads, dtype=float64).reshape((-1, 3))
        A = weighted_product(C, Q, C)
        Ai = weighted_product(Ci, Q, Ci)
        Af = weighted_product(Ci, Q, Cf)
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

    def update_forcedensities(self, edges: list[int], newqs: Sequence[float] | FloatArray) -> None:
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
        Ci = cast(csr_matrix, C[:, self.free])
        Cf = cast(csr_matrix, C[:, self.fixed])
        self.q[edges] = newqs
        self.Q = diagonal(self.q)  # pyright: ignore[reportConstantRedefinition]
        self.A = weighted_product(C, self.Q, C)  # pyright: ignore[reportConstantRedefinition]
        self.Ai = weighted_product(Ci, self.Q, Ci)
        self.Af = weighted_product(Ci, self.Q, Cf)
