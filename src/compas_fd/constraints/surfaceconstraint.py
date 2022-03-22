from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import NurbsSurface
from .constraint import Constraint

import compas
if compas.IPY:  # Tom: is this allowed?
    from compas_rhino.geometry import RhinoSurface


class SurfaceConstraint(Constraint):

    def __init__(self, surface, **kwargs):
        super(SurfaceConstraint, self).__init__(geometry=surface, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data, 'guid': str(self.guid)}

    @data.setter
    def data(self, data):
        self.geometry = NurbsSurface.from_data(data['geometry'])
        self.guid = data['guid']

    @classmethod
    def from_data(cls, data):
        srf = NurbsSurface.from_data(data['geometry'])
        constraint = cls(srf)
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
        self._tangent = self.residual - self.normal

    def compute_normal(self):
        _, _, _, normal = self.geometry.curvature_at(*self._param)
        self._normal = Vector(*vector_component(self.residual, normal))

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping
        pt_on_srf = self.geometry.closest_point(self._location, return_parameters=False)
        if self._location.distance_to_point(pt_on_srf) > 0.001:
            self.project()

    def project(self):
        xyz, self._param = self.geometry.closest_point(self._location, return_parameters=True)
        self._location = Point(* xyz)

    def compute_param(self):
        _, self._param = self.geometry.closest_point(self._location, return_parameters=True)

    def update_location_at_param(self):
        self._location = self.geometry.point_at(*self._param)

    def update_geometry_guid(self):
        self._geometry = RhinoSurface.from_guid(self._guid).to_compas()

    @property
    def rhinogeometry(self):
        self._rhinogeometry = RhinoSurface.from_guid(self._guid).geometry
        return self._rhinogeometry
