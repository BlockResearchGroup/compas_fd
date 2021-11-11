from typing import Sequence

from numpy import asarray
from numpy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas.numerical import normrow

from .solver import Solver
from ..numdata import FDNumericalData
from ..constraints import Constraint


class FDConstraintSolver(Solver):
    """Manager class for running iterative constraint force density algorithm,
    updating numerical data and storing results.
    """

    def __init__(self,
                 numdata: FDNumericalData,
                 constraints: Sequence[Constraint] = None,
                 max_iter: int = 100,
                 tol_dxyz: float = 1E-3,
                 tol_res: float = 1E-3,
                 **kwargs
                 ) -> None:
        super(FDConstraintSolver, self).__init__(numdata, max_iter, **kwargs)
        self.constraints = constraints
        self.tol_dxyz = tol_dxyz
        self.tol_res = tol_res

    def solve(self) -> None:
        """Apply force density algorithm for a single iteration."""
        free, fixed, xyz, C, q, Q, p, A, Ai, Af, *_ = self.numdata
        b = p[free] - Af.dot(xyz[fixed])
        xyz[free] = spsolve(Ai, b)
        self.numdata.residuals = p - A.dot(xyz)
        self.numdata.xyz_prev = xyz.copy()
        self.numdata.xyz = xyz
        self._update_constraints()

    def _update_constraints(self):
        """Update all vertex constraints by the residuals of the current iteration,
        and store their updated vertex coordinates in the numdata attribute.
        """
        xyz = self.numdata.xyz
        residuals = self.numdata.residuals
        for vertex, constraint in enumerate(self.constraints):
            if not constraint:
                continue
            constraint.location = xyz[vertex]
            constraint.residual = residuals[vertex]
            xyz[vertex] = constraint.location + constraint.tangent * 0.5
        self.numdata.tangent_residuals = asarray([c.tangent for c in self.constraints if c])
        self.numdata.xyz = xyz

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        return self._is_converged_residuals and self._is_converged_xyz

    @property
    def _is_converged_residuals(self) -> bool:
        """Verify whether the maximum constraint residual is within tolerance."""
        residuals = self.numdata.tangent_residuals
        if residuals is None or not residuals.any():
            return True
        max_res = max(norm(residuals, axis=1))
        return max_res < self.tol_res

    @property
    def _is_converged_xyz(self) -> bool:
        """Verify whether the maximum coordinate displacement
        between consecutive iterations is within tolerance.
        """
        new_xyz = self.numdata.xyz
        old_xyz = self.numdata.xyz_prev
        max_dxyz = max(norm(new_xyz - old_xyz, axis=1))
        return max_dxyz < self.tol_dxyz

    def post_process(self) -> None:
        """Compute dependent variables after ending the solver loop."""
        _, _, xyz, C, q, *_ = self.numdata
        lengths = normrow(C.dot(xyz))
        self.numdata.forces = q * lengths
        self.numdata.lengths = lengths
