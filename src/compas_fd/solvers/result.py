from typing import List
from typing import NamedTuple

from compas_fd.types import FloatNx3


class Result(NamedTuple):
    vertices: FloatNx3
    residuals: FloatNx3
    forces: List[float]
    lengths: List[float]

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["vertices"],
            data["residuals"],
            data["forces"],
            data["lengths"],
        )
