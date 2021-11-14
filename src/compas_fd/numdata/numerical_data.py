from dataclasses import dataclass
from dataclasses import astuple

from compas_fd.result import Result


@dataclass
class NumericalData:
    """Storage class for numerical arrays used by solver algorithms."""

    def __iter__(self):
        return iter(astuple(self))

    @classmethod
    def from_params(cls, *args, **kwargs):
        """Construct nuerical arrays from algorithm input parameters."""
        raise NotImplementedError

    @classmethod
    def from_mesh(cls, mesh):
        """Construct numerical arrays from input mesh."""
        raise NotImplementedError

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        raise NotImplementedError
