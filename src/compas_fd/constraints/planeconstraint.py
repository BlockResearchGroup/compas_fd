from __future__ import annotations

from typing import Any
from typing import Self
from typing import cast

from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import project_point_plane

from .constraint import Constraint


class PlaneConstraint(Constraint[Plane]):
    """Constraint for limiting the movement of a vertex to a plane."""

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        plane = Plane.__from_data__(data["geometry"])
        constraint = cls(plane)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self) -> None:
        self._tangent = cast(Vector, self.residual) - self.normal

    def compute_normal(self) -> None:
        normal = self.geometry.normal
        self._normal = self._project_residual(normal)

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping

    def project(self) -> None:
        plane = (tuple(self.geometry.point), tuple(self.geometry.normal))
        x, y, z = project_point_plane(tuple(cast(Point, self._location)), plane)
        self._location = Point(x, y, z)
