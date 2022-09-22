from typing import Tuple
from typing import List
from typing import Union
from typing import Sequence
from typing import Optional
from typing_extensions import Literal
from typing_extensions import Annotated
from nptyping import NDArray
from nptyping import Float64
from nptyping import Int32

from dataclasses import dataclass
from dataclasses import astuple

from numpy import asarray
from numpy import float64
from numpy import zeros_like
from scipy.sparse import diags

from compas.numerical import connectivity_matrix
from compas_fd.fd.result import Result

FloatNx3 = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Literal["*, 3"], Float64],
]


@dataclass
class FDNumericalData:
    """
    Stores numerical data used by the force density algorithms.
    """

    free: int
    fixed: int
    xyz: NDArray[Literal["*, 3"], Float64]
    C: NDArray[Literal["*, *"], Int32]
    q: NDArray[Literal["*, 1"], Float64]
    Q: NDArray[Literal["*, *"], Float64]
    p: NDArray[Literal["*, 1"], Float64]
    A: NDArray[Literal["*, *"], Float64]
    Ai: NDArray[Literal["*, *"], Float64]
    Af: NDArray[Literal["*, *"], Float64]
    forces: NDArray[Literal["*, 1"], Float64] = None
    lengths: NDArray[Literal["*, 1"], Float64] = None
    residuals: NDArray[Literal["*, 3"], Float64] = None
    tangent_residuals: NDArray[Literal["*, 3"], Float64] = None
    normal_residuals: NDArray[Literal["*, 1"], Float64] = None

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
    ):
        """
        Construct numerical arrays from force density solver input parameters.
        """
        free = list(set(range(len(vertices))) - set(fixed))
        xyz = asarray(vertices, dtype=float64).reshape((-1, 3))
        C = connectivity_matrix(edges, "csr")
        Ci = C[:, free]
        Cf = C[:, fixed]
        q = asarray(forcedensities, dtype=float64).reshape((-1, 1))
        Q = diags([q.flatten()], [0])
        p = (
            zeros_like(xyz)
            if loads is None
            else asarray(loads, dtype=float64).reshape((-1, 3))
        )
        A = C.T.dot(Q).dot(C)
        Ai = Ci.T.dot(Q).dot(Ci)
        Af = Ci.T.dot(Q).dot(Cf)
        return cls(free, fixed, xyz, C, q, Q, p, A, Ai, Af)

    @classmethod
    def from_mesh(cls, mesh):
        """
        Construct numerical arrays from input mesh.
        """
        raise NotImplementedError

    def to_result(self) -> Result:
        """
        Parse relevant numerical data into a Result object.
        """
        return Result(self.xyz, self.residuals, self.forces, self.lengths)

    def update_forcedensities(self, edges, newqs):
        C = self.C
        Ci = C[:, self.free]
        Cf = C[:, self.fixed]
        self.q[edges] = newqs
        self.Q = diags([self.q.flatten()], [0])
        self.A = C.T.dot(self.Q).dot(C)
        self.Ai = Ci.T.dot(self.Q).dot(Ci)
        self.Af = Ci.T.dot(self.Q).dot(Cf)
