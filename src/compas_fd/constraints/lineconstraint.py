from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import closest_point_on_segment
from compas.geometry import is_point_on_segment
from compas.geometry import vector_component

from .constraint import Constraint


class LineConstraint(Constraint):
    """Constraint for limiting the movement of a vertex to a line."""

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "geometry": Line.DATASCHEMA,
            "rhino_guid": {"type": "string"},
        },
        "required": ["geometry"],
    }

    @classmethod
    def __from_data__(cls, data):
        line = Line.__from_data__(data["geometry"])
        constraint = cls(line)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        if not is_point_on_segment(point=self._location, segment=self._geometry):
            self.project()

    def project(self):
        self._location = Point(*closest_point_on_segment(self._location, self.geometry))

    def compute_param(self):
        v = Vector.from_start_end(self._geometry.start, self._location)
        u = self._geometry.vector
        d = v.dot(u)
        if not d == 0:
            d = d / abs(d)
        self._param = v.length * d

    def update_location_at_param(self):
        d = self._geometry.direction
        self._location = self._geometry.start + d * self._param
