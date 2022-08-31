from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Frame
from .constraint import Constraint


class FrameConstraint(Constraint):
    def __init__(self, frame, **kwargs):
        super(FrameConstraint, self).__init__(geometry=frame, **kwargs)

    @property
    def data(self):
        return {
            "geometry": self.geometry.data,
            "rhino_guid": str(self._rhino_guid),
        }

    @data.setter
    def data(self, data):
        self.geometry = Frame.from_data(data["geometry"])
        self._rhino_guid = str(data["rhino_guid"])

    @classmethod
    def from_data(cls, data):
        frame = Frame.from_data(data["geometry"])
        constraint = cls(frame)
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
