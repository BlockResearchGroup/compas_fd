from typing import Any
from typing import Self
from typing import cast

from compas.geometry import Point
from compas.geometry import Vector

from .constraint import Constraint


class VectorConstraint(Constraint[Vector]):
    """Constraint for limiting the movement of a vertex to a vector."""

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        vector = Vector.__from_data__(data["geometry"]).unitized()
        constraint = cls(vector)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self) -> None:
        self._tangent = self._project_residual(self.geometry)

    def compute_normal(self) -> None:
        self._normal = cast(Vector, self.residual) - self.tangent

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping

    def project(self) -> None:
        pass
