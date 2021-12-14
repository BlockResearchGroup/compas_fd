from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import inspect

from compas.data import Data
from compas.geometry import Vector
from compas.geometry import Point

from .exceptions import GeometryNotRegisteredAsConstraint


class Constraint(Data):

    GEOMETRY_CONSTRAINT = {}

    @staticmethod
    def get_constraint_cls(geometry, **kwargs):
        gtype = type(geometry)
        cls = None
        for type_ in inspect.getmro(gtype):
            cls = Constraint.GEOMETRY_CONSTRAINT.get(type_)
            if cls is not None:
                break
        if cls is None:
            raise GeometryNotRegisteredAsConstraint('No constraint is registered for this geometry type: {}'.format(gtype))
        return cls

    def __new__(cls, *args, **kwargs):
        geometry = args[0]
        cls = Constraint.get_constraint_cls(geometry)
        return super(Constraint, cls).__new__(cls)

    def __init__(self, geometry, **kwargs):
        super(Constraint, self).__init__(**kwargs)
        self._geometry = None
        self._location = None
        self._residual = None
        self._tangent = None
        self._normal = None
        self._guid = None
        self._param = None
        self._rhinogeometry = None
        self.geometry = geometry

    @staticmethod
    def register(gtype, ctype):
        Constraint.GEOMETRY_CONSTRAINT[gtype] = ctype

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, geometry):
        self._residual = None
        self._tangent = None
        self._normal = None
        self._geometry = geometry

    @property
    def guid(self):
        return self._guid

    @guid.setter
    def guid(self, guid):
        self._guid = guid

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, point):
        self._tangent = None
        self._normal = None
        self._location = Point(*point)
        if not getattr(self, 'projected', None):
            self.project()
            self.projected = True

    @property
    def residual(self):
        return self._residual

    @residual.setter
    def residual(self, residual):
        self._tangent = None
        self._normal = None
        self._residual = Vector(*residual)

    def compute_tangent(self):
        raise NotImplementedError

    def compute_normal(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def compute_param(self):
        raise NotImplementedError

    def project(self):
        raise NotImplementedError

    def update_location_at_param(self):
        raise NotImplementedError

    def update_geometry_guid(self):
        raise NotImplementedError

    @property
    def tangent(self):
        if self._tangent is None:
            self.compute_tangent()
        return self._tangent

    @property
    def normal(self):
        if self._normal is None:
            self.compute_normal()
        return self._normal

    @property
    def param(self):
        if self._param is None:
            self.compute_param()
        return self._param

    @property
    def rhinogeometry(self):
        raise NotImplementedError
