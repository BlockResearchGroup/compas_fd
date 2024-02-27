from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import vector_component

from .constraint import Constraint


class CircleConstraint(Constraint):
    """Constraint for limiting the movement of a vertex to a circle."""

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "geometry": Circle.DATASCHEMA,
            "rhino_guid": {"type": "string"},
        },
        "required": ["geometry"],
    }

    @classmethod
    def __from_data__(cls, data):
        circle = Circle.__from_data__(data["geometry"])
        curve = NurbsCurve.from_circle(circle)
        constraint = cls(curve)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, point):
        self._tangent = None
        self._normal = None
        self._location = Point(*point)
        self.project()

    def compute_tangent(self):
        direction = self.geometry.tangent_at(self._param)
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        pt_on_curve = self.geometry.closest_point(self._location, return_parameter=False)
        if self._location.distance_to_point(pt_on_curve) > 0.001:
            self.project()

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, return_parameter=True)
        self._location = Point(*xyz)

    def compute_param(self):
        _, self._param = self.geometry.closest_point(self._location, return_parameter=True)

    def update_location_at_param(self):
        self._location = self.geometry.point_at(self._param)
