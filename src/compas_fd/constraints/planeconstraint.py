from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from .constraint import Constraint
from compas.geometry import Vector
from compas.geometry import vector_component


class PlaneConstraint(Constraint):

    def __init__(self, plane, index, **kwargs):
        super(PlaneConstraint, self).__init__(geometry=plane, index=index, **kwargs)

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        normal = self.geometry.normal
        self._normal = Vector(* vector_component(self.residual, normal))

    def project_to_geometry(self):
        origin = self.geometry.point
        normal = self.geometry.normal
        vec_to_origin = origin - self.location
        self._location += Vector(* vector_component(vec_to_origin, normal))
