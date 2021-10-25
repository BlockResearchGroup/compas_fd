from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Frame
from .constraint import Constraint


class LineConstraint(Constraint):

    def __init__(self, line, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, **kwargs)

    def compute_components(self):
        o = self.location
        y = self.residual
        x = self.geometry.direction
        frame = Frame(o, x, y)
        tangent = Vector(* vector_component(self.residual, frame.xaxis))
        normal = Vector(* vector_component(self.residual, frame.yaxis))
        self._tangent = tangent
        self._normal = normal
