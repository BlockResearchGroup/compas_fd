from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import project_point_line
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Line
from .constraint import Constraint


class LineConstraint(Constraint):

    def __init__(self, line, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data}

    @data.setter
    def data(self, data):
        self.geometry = Line.from_data(data['geometry'])

    @classmethod
    def from_data(cls, data):
        line = Line.from_data(data['geometry'])
        return cls(line)

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project(self):
        self._location = Point(*project_point_line(self._location, self.geometry))
