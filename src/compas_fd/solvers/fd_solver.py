from scipy.sparse.linalg import spsolve

from compas_fd.numdata import FDNumericalData
from .solver import Solver


class FDSolver(Solver):
    """Manager class for running a single step force density algorithm,
    updating numerical data and storing results.
    """

    def __init__(self, numdata: FDNumericalData, **kwargs) -> None:
        super(FDSolver, self).__init__(numdata, 1, **kwargs)

    def solve(self) -> None:
        """Apply force density algorithm for a single iteration."""
        nd = self.numdata
        b = nd.p[nd.free] - nd.Df.dot(nd.xyz[nd.fixed])
        nd.xyz[nd.free] = spsolve(nd.Di, b)

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        return True
