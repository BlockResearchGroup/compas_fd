from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from .constraint import Constraint


class CurveConstraint(Constraint):

    def __init__(self, curve, **kwargs):
        super(CurveConstraint, self).__init__(geometry=curve, **kwargs)

    def compute_tangent(self):
        direction = self.geometry.tangent_at(self._param)
        self._tangent = Vector(* vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, parameter=True)
        self._location = Point(* xyz)
