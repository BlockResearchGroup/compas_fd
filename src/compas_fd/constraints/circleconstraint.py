from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Circle

from .constraint import Constraint


class CircleConstraint(Constraint):
    def __init__(self, curve, **kwargs):
        super(CircleConstraint, self).__init__(geometry=curve, **kwargs)

    @property
    def data(self):
        return {
            "geometry": self.geometry.data,
            "rhino_guid": str(self._rhino_guid),
        }

    @data.setter
    def data(self, data):
        self.geometry = Circle.from_data(data["geometry"])
        self._rhino_guid = str(data["rhino_guid"])

    @classmethod
    def from_data(cls, data):
        curve = Circle.from_data(data["geometry"])
        constraint = cls(curve)
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
        direction = self.geometry.tangent_at(self.location)
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        point = self.geometry.closest_point(self.location)
        if self._location.distance_to_point(point) > 0.001:
            self.project()

    def project(self):
        point = self.geometry.closest_point(self.location)
        self._location = point
