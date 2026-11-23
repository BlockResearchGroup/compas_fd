from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from typing import Self
from typing import cast

from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Vector

from ._dataschemas import SURFACE
from ._dataschemas import constraint_schema
from .constraint import Constraint


class SurfaceConstraint(Constraint[NurbsSurface]):
    """Constraint for limiting the movement of a vertex to a surface."""

    DATASCHEMA = constraint_schema(SURFACE)

    @property
    def __data__(self) -> dict[str, Any]:
        data = super().__data__
        geometry = data["geometry"].copy()
        if "control_points" in geometry:
            geometry["points"] = geometry.pop("control_points")
        data["geometry"] = geometry
        return data

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        geometry = data["geometry"].copy()
        if "control_points" not in geometry and "points" in geometry:
            geometry["control_points"] = geometry.pop("points")
        srf = NurbsSurface.__from_data__(geometry)
        constraint = cls(srf)
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
        self._tangent = cast(Vector, self.residual) - self.normal

    def compute_normal(self) -> None:
        normal = self.geometry.normal_at(*cast("tuple[float, float]", self._param))
        self._normal = self._project_residual(normal)

    def update(self, damping: float = 0.1) -> None:
        self._location = cast(Point, self.location) + self.tangent * damping
        pt_on_srf = self.geometry.closest_point(self._location, return_parameters=False)
        if self._location.distance_to_point(cast(Point, pt_on_srf)) > 0.001:
            self.project()

    def project(self) -> None:
        # These methods require a backend that can project the point.
        closest = self.geometry.closest_point(cast(Point, self._location), return_parameters=True)
        xyz, self._param = cast("tuple[Point, tuple[float, float]]", closest)
        self._location = Point(*cast("tuple[float, float, float]", xyz))

    def compute_param(self) -> None:
        closest = self.geometry.closest_point(cast(Point, self._location), return_parameters=True)
        _, self._param = cast("tuple[Point, tuple[float, float]]", closest)

    def update_location_at_param(self) -> None:
        self._location = self.geometry.point_at(*cast("tuple[float, float]", self._param))
