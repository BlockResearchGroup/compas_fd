from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from .constraint import Constraint


class SurfaceConstraint(Constraint):

    def __init__(self, surface, **kwargs):
        super(SurfaceConstraint, self).__init__(geometry=surface, **kwargs)

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        _, _, _, normal = self.geometry.curvature_at(* self._param)
        print(normal)
        self._normal = Vector(* vector_component(self.residual, normal))

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, parameter=True)
        self._location = Point(* xyz)
