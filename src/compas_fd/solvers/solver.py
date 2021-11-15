from compas_fd.numdata import NumericalData
from compas_fd.result import Result


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
        self.kcount = 0
        self.result = None

    def __call__(self) -> Result:
        """Iteratively apply the solver algorithm."""
        for self.kcount in range(1, self.kmax + 1):
            self.solve()
            if self.is_converged:
                break
        self.post_process()
        self.result = self.numdata.to_result()
        return self.result

    def solve(self) -> None:
        """Apply the solver algorithm for a single iteration."""
        raise NotImplementedError

    @property
    def is_converged(self) -> bool:
        """Verify if convergence criteria are met."""
        raise NotImplementedError

    def post_process(self) -> None:
        """Callable after ending the solver loop."""
        pass
