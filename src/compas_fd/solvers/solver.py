from ..numdata import NumericalData
from ..result import Result


class Solver:
    """Manager class for running iterative algorithms,
    updating numerical data and storing results.
    """

    def __init__(self,
                 numdata: NumericalData,
                 kmax: int = 100,
                 **kwargs
                 ) -> None:
        self.numdata = numdata
        self.kmax = kmax
        self.iter_count = 0
        self.result = None

    def __call__(self) -> Result:
        """Iteratively apply the solver algorithm."""
        for self.iter_count in range(1, self.kmax + 1):
            self.solve()
            if self.is_converged:
                break
        self.post_process()
        self.result = self.numdata.to_result()
        return self.result

    def solve(self) -> None:
        """Apply solver algorithm for a single iteration."""
        raise NotImplementedError

    @property
    def is_converged(self) -> bool:
        """Verify if all convergence criteria are met."""
        raise NotImplementedError

    def post_process(self) -> None:
        """Compute dependent variables after ending the solver loop."""
        raise NotImplementedError
