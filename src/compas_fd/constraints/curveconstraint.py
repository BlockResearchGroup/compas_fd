from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from typing import Self
from typing import cast

from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Vector

from ._dataschemas import CURVE
from ._dataschemas import constraint_schema
from .constraint import Constraint


class CurveConstraint(Constraint[NurbsCurve]):
    """Constraint for limiting the movement of a vertex to a Nurbs curve."""

    DATASCHEMA = constraint_schema(CURVE)

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        curve = NurbsCurve.__from_data__(data["geometry"])
        constraint = cls(curve)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    @property
    def location(self) -> Point | None:
        return self._location

    @location.setter
    def location(self, point: Iterable[float]) -> None:
        self._tangent = None
        self._normal = None
        self._location = Point(*cast("tuple[float, float, float]", point))
        self.project()

    def compute_tangent(self) -> None:
        direction = self.geometry.tangent_at(cast(float, self._param))
        self._tangent = self._project_residual(direction)

    def compute_normal(self) -> None:
        self._normal = cast(Vector, self.residual) - self.tangent

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping
        pt_on_curve = self.geometry.closest_point(self._location, return_parameter=False)
        if self._location.distance_to_point(pt_on_curve) > 0.001:
            self.project()

    def project(self) -> None:
        xyz, self._param = self.geometry.closest_point(cast(Point, self._location), return_parameter=True)
        self._location = Point(*cast("tuple[float, float, float]", xyz))

    def compute_param(self) -> None:
        _, self._param = self.geometry.closest_point(cast(Point, self._location), return_parameter=True)

    def update_location_at_param(self) -> None:
        self._location = self.geometry.point_at(cast(float, self._param))
