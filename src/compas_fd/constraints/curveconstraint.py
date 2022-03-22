from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import NurbsCurve
from .constraint import Constraint

import compas
if compas.IPY:  # Tom: is this allowed?
    from compas_rhino.geometry import RhinoCurve


class CurveConstraint(Constraint):

    def __init__(self, curve, **kwargs):
        super(CurveConstraint, self).__init__(geometry=curve, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data, 'guid': str(self.guid)}

    @data.setter
    def data(self, data):
        self.geometry = NurbsCurve.from_data(data['geometry'])
        self.guid = data['guid']

    @classmethod
    def from_data(cls, data):
        curve = NurbsCurve.from_data(data['geometry'])
        constraint = cls(curve)
        constraint.guid = data['guid']
        return constraint

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

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        pt_on_curve = self.geometry.closest_point(self._location, return_parameter=False)
        if self._location.distance_to_point(pt_on_curve) > 0.001:
            self.project()

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, return_parameter=True)
        self._location = Point(* xyz)

    def compute_param(self):
        _, self._param = self.geometry.closest_point(self._location, return_parameter=True)

    def update_location_at_param(self):
        self._location = self.geometry.point_at(self._param)

    def update_geometry_guid(self):
        self._geometry = RhinoCurve.from_guid(self._guid).to_compas()

    @property
    def rhinogeometry(self):
        self._rhinogeometry = RhinoCurve.from_guid(self._guid).geometry
        return self._rhinogeometry
