from __future__ import annotations

from typing import Any
from typing import Self
from typing import cast

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import closest_point_on_segment
from compas.geometry import is_point_on_segment

from ._dataschemas import LINE
from ._dataschemas import constraint_schema
from .constraint import Constraint


class LineConstraint(Constraint[Line]):
    """Constraint for limiting the movement of a vertex to a line."""

    DATASCHEMA = constraint_schema(LINE)

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        line = Line.__from_data__(data["geometry"])
        constraint = cls(line)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self) -> None:
        direction = self.geometry.direction
        self._tangent = self._project_residual(direction)

    def compute_normal(self) -> None:
        self._normal = cast(Vector, self.residual) - self.tangent

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping
        if not is_point_on_segment(point=self._location, segment=self._geometry):
            self.project()

    def project(self) -> None:
        xyz = closest_point_on_segment(cast(Point, self._location), self.geometry)
        self._location = Point(*cast("tuple[float, float, float]", xyz))

    def compute_param(self) -> None:
        v = Vector.from_start_end(self._geometry.start, cast(Point, self._location))
        u = self._geometry.vector
        d = v.dot(u)
        if not d == 0:
            d = d / abs(d)
        self._param = v.length * d

    def update_location_at_param(self) -> None:
        d = self._geometry.direction
        self._location = self._geometry.start + d * cast(float, self._param)
