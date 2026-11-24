from typing import Any
from typing import Self
from typing import cast

from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Vector

from .constraint import Constraint


class FrameConstraint(Constraint[Frame]):
    """Constraint for limiting the movement of a vertex to a frame."""

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        frame = Frame.__from_data__(data["geometry"])
        constraint = cls(frame)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self) -> None:
        self._tangent = cast(Vector, self.residual) - self.normal

    def compute_normal(self) -> None:
        normal = self.geometry.zaxis
        self._normal = self._project_residual(normal)

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping

    def project(self) -> None:
        pass
