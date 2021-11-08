from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import project_point_plane
from .constraint import Constraint


class PlaneConstraint(Constraint):

    def __init__(self, plane, **kwargs):
        super(PlaneConstraint, self).__init__(geometry=plane, **kwargs)

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        normal = self.geometry.normal
        self._normal = Vector(* vector_component(self.residual, normal))

    def project(self):
        self._location = Point(* project_point_plane(self._location, self.geometry))
