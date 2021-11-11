from scipy.sparse.linalg import spsolve

from compas.numerical import normrow

from .solver import Solver
from ..numdata import FDNumericalData


class FDSolver(Solver):
    """Manager class for running a single step force density algorithm,
    updating numerical data and storing results.
    """

    def __init__(self, numdata: FDNumericalData, **kwargs) -> None:
        super(FDSolver, self).__init__(numdata, 1, **kwargs)

    def solve(self) -> None:
        """Apply force density algorithm for a single iteration."""
        free, fixed, xyz, C, q, Q, p, _, Ai, Af, *_ = self.numdata
        b = p[free] - Af.dot(xyz[fixed])
        xyz[free] = spsolve(Ai, b)
        self.numdata.xyz = xyz

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        return True

    def post_process(self) -> None:
        """Compute dependent variables after ending solver."""
        _, _, xyz, C, q, Q, p, A, *_ = self.numdata
        lengths = normrow(C.dot(xyz))
        self.numdata.lengths = lengths
        self.numdata.forces = q * lengths
        self.numdata.residuals = p - A.dot(xyz)
