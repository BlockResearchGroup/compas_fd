from collections.abc import Sequence
from typing import NamedTuple
from typing import TypedDict

from compas_fd.types import FloatNx1
from compas_fd.types import FloatNx3


class _ResultDict(TypedDict):
    vertices: FloatNx3
    residuals: FloatNx3 | None
    forces: FloatNx1 | Sequence[float] | None
    lengths: FloatNx1 | Sequence[float] | None


class Result(NamedTuple):
    """Equilibrium coordinates, residual forces, axial forces, and edge lengths.

    Attributes
    ----------
    vertices : FloatNx3
        Equilibrium coordinates of shape `(n, 3)` in vertex order.
    residuals : FloatNx3 or None
        Residual forces of shape `(n, 3)` in vertex order, when available.
    forces : FloatNx1 or None
        Axial forces of shape `(m, 1)` in edge order, when available.
    lengths : FloatNx1 or None
        Edge lengths of shape `(m, 1)` in edge order, when available.
    """

    vertices: FloatNx3
    residuals: FloatNx3 | None
    forces: FloatNx1 | Sequence[float] | None
    lengths: FloatNx1 | Sequence[float] | None

    @classmethod
    def from_dict(cls, data: _ResultDict) -> "Result":
        """Construct a result from its fields, preserving supplied array or list values."""
        return cls(
            data["vertices"],
            data["residuals"],
            data["forces"],
            data["lengths"],
        )
