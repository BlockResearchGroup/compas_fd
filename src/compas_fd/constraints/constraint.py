from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data
from compas.geometry import Vector
from compas.geometry import Point


class Constraint(Data):

    GEOMETRY_CONSTRAINT = {}

    @property
    def DATASCHEMA(self):
        from schema import Schema
        return Schema()

    @property
    def JSONSCHEMANAME(self):
        return 'constraint'

    @property
    def data(self):
        return {}

    @data.setter
    def data(self, data):
        pass

    @classmethod
    def from_data(cls, data):
        return cls()

    def __new__(cls, *args, **kwargs):
        geometry = args[0]
        cls = Constraint.GEOMETRY_CONSTRAINT[type(geometry)]
        return super(Constraint, cls).__new__(cls)

    def __init__(self, geometry, **kwargs):
        super(Constraint, self).__init__(**kwargs)
        self._geometry = None
        self._residual = None
        self._tangent = None
        self._normal = None
        self.geometry = geometry

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
    def location(self):
        return self._location

    @location.setter
    def location(self, point):
        self._tangent = None
        self._normal = None
        self._location = Point(*point)

    @property
    def residual(self):
        return self._residual

    @residual.setter
    def residual(self, residual):
        self._tangent = None
        self._normal = None
        self._residual = Vector(*residual)

    def compute_components(self):
        raise NotImplementedError

    @property
    def tangent(self):
        if self._tangent is None:
            self.compute_components()
        return self._tangent

    @property
    def normal(self):
        if self._normal is None:
            self.compute_components()
        return self._normal