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
        nd = self.numdata
        b = nd.p[nd.free] - nd.Af.dot(nd.xyz[nd.fixed])
        nd.xyz[nd.free] = spsolve(nd.Ai, b)

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        return True

    def post_process(self) -> None:
        """Compute dependent variables after ending solver."""
        nd = self.numdata
        nd.lengths = normrow(nd.C.dot(nd.xyz))
        nd.forces = nd.q * nd.lengths
        nd.residuals = nd.p - nd.A.dot(nd.xyz)
