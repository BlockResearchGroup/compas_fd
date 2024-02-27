from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Vector
from compas.geometry import vector_component

from .constraint import Constraint


class VectorConstraint(Constraint):
    """Constraint for limiting the movement of a vertex to a vector."""

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "geometry": Vector.DATASCHEMA,
            "rhino_guid": {"type": "string"},
        },
        "required": ["geometry"],
    }

    @classmethod
    def __from_data__(cls, data):
        vector = Vector.__from_data__(data["geometry"]).unitized()
        constraint = cls(vector)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self):
        self._tangent = Vector(*vector_component(self.residual, self.geometry))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping

    def project(self):
        pass
