from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import NurbsCurve
from .constraint import Constraint


class CurveConstraint(Constraint):

    def __init__(self, curve, **kwargs):
        super(CurveConstraint, self).__init__(geometry=curve, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data}

    @data.setter
    def data(self, data):
        self.geometry = NurbsCurve.from_data(data['geometry'])

    @classmethod
    def from_data(cls, data):
        curve = NurbsCurve.from_data(data['geometry'])
        return cls(curve)

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
        direction = self.geometry.tangent_at(self._param)
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, return_parameter=True)
        self._location = Point(* xyz)
