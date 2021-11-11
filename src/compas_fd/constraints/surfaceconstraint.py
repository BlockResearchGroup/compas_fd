from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import NurbsSurface
from .constraint import Constraint


class SurfaceConstraint(Constraint):

    def __init__(self, surface, **kwargs):
        super(SurfaceConstraint, self).__init__(geometry=surface, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data}

    @data.setter
    def data(self, data):
        self.geometry = NurbsSurface.from_data(data['geometry'])

    @classmethod
    def from_data(cls, data):
        srf = NurbsSurface.from_data(data['geometry'])
        return cls(srf)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, point):
        self._tangent = None
        self._normal = None
        self._location = Point(*point)
        self.project()

    def compute_tangent(self):
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        _, _, _, normal = self.geometry.curvature_at(*self._param)
        self._normal = Vector(*vector_component(self.residual, normal))

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, return_parameter=True)
        self._location = Point(* xyz)
