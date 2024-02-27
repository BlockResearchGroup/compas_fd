from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import project_point_plane
from compas.geometry import vector_component

from .constraint import Constraint


class PlaneConstraint(Constraint):
    """Constraint for limiting the movement of a vertex to a plane."""

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "geometry": Plane.DATASCHEMA,
            "rhino_guid": {"type": "string"},
        },
        "required": ["geometry"],
    }

    @classmethod
    def __from_data__(cls, data):
        plane = Plane.__from_data__(data["geometry"])
        constraint = cls(plane)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        normal = self.geometry.normal
        self._normal = Vector(*vector_component(self.residual, normal))

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping

    def project(self):
        self._location = Point(*project_point_plane(self._location, self.geometry))
