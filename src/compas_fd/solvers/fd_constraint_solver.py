from typing import Sequence

from numpy import asarray
from numpy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas.numerical import normrow

from compas_fd.numdata import FDNumericalData
from compas_fd.constraints import Constraint
from .solver import Solver


class FDConstraintSolver(Solver):
    """Manager class for running iterative constraint force density algorithm,
    updating numerical data and storing results.
    """

    def __init__(self,
                 numdata: FDNumericalData,
                 constraints: Sequence[Constraint] = None,
                 kmax: int = 100,
                 tol_res: float = 1E-3,
                 tol_disp: float = 1E-3,
                 **kwargs
                 ) -> None:
        super(FDConstraintSolver, self).__init__(numdata, kmax, **kwargs)
        self.constraints = constraints
        self.tol_res = tol_res
        self.tol_disp = tol_disp

    def solve(self) -> None:
        """Apply force density algorithm for a single iteration."""
        nd = self.numdata
        b = nd.p[nd.free] - nd.Af.dot(nd.xyz[nd.fixed])
        nd.xyz[nd.free] = spsolve(nd.Ai, b)
        nd.residuals = nd.p - nd.A.dot(nd.xyz)
        nd.xyz_prev = nd.xyz.copy()
        self._update_constraints()

    def _update_constraints(self):
        """Update all vertex constraints by the residuals of the current iteration,
        and store their updated vertex coordinates in the numdata attribute.
        """
        nd = self.numdata
        for vertex, constraint in enumerate(self.constraints):
            if not constraint:
                continue
            constraint.location = nd.xyz[vertex]
            constraint.residual = nd.residuals[vertex]
            nd.xyz[vertex] = constraint.location + constraint.tangent * 0.5
        nd.tangent_residuals = asarray([c.tangent for c in self.constraints if c])

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        return (self._is_converged_residuals and
                self._is_converged_displacements)

    @property
    def _is_converged_residuals(self) -> bool:
        """Verify whether the maximum constraint residual is within tolerance."""
        residuals = self.numdata.tangent_residuals
        if residuals is None or not residuals.any():
            return True
        max_res = max(norm(residuals, axis=1))
        return max_res < self.tol_res

    @property
    def _is_converged_displacements(self) -> bool:
        """Verify whether the maximum coordinate displacement
        between consecutive iterations is within tolerance.
        """
        nd = self.numdata
        max_dxyz = max(norm(nd.xyz - nd.xyz_prev, axis=1))
        return max_dxyz < self.tol_disp

    def post_process(self) -> None:
        """Compute dependent variables after ending the solver loop."""
        nd = self.numdata
        nd.lengths = normrow(nd.C.dot(nd.xyz))
        nd.forces = nd.q * nd.lengths
