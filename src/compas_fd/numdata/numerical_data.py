from compas_fd.result import Result


class NumericalData:
    """Storage class for numerical arrays used by solver algorithms."""

    @classmethod
    def from_mesh(cls, mesh):
        """Construct numerical arrays from input mesh."""
        raise NotImplementedError

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        raise NotImplementedError
