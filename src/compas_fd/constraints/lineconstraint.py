from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .constraint import Constraint
from compas.geometry import Vector
from compas.geometry import vector_component


class LineConstraint(Constraint):

    def __init__(self, line, index, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, index=index, **kwargs)

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(* vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project_to_geometry(self):
        origin = self.geometry.start
        direction = self.geometry.direction
        vec_to_origin = origin - self.location
        self._location = origin - Vector(* vector_component(vec_to_origin, direction))
