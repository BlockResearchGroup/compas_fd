from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import project_point_line
from compas.geometry import Vector
from compas.geometry import Point
from .constraint import Constraint


class LineConstraint(Constraint):

    def __init__(self, line, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, **kwargs)

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(* vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project(self):
        self._location = Point(* project_point_line(self._location, self.geometry))
