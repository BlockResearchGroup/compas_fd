from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.geometry import Frame
from compas.geometry import Vector
from compas.geometry import vector_component

from .constraint import Constraint


class FrameConstraint(Constraint):
    """Constraint for limiting the movement of a vertex to a frame."""

    DATASCHEMA = {
        "type": "object",
        "properties": {
            "geometry": Frame.DATASCHEMA,
            "rhino_guid": {"type": "string"},
        },
        "required": ["geometry"],
    }

    @classmethod
    def __from_data__(cls, data):
        frame = Frame.__from_data__(data["geometry"])
        constraint = cls(frame)
        if "rhino_guid" in data:
            constraint._rhino_guid = str(data["rhino_guid"])
        return constraint

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        normal = self.geometry.zaxis
        self._normal = Vector(*vector_component(self.residual, normal))

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping

    def project(self):
        pass
