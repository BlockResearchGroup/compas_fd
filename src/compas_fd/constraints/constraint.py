from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Point
from compas.data import Data


class Constraint(Data):

    GEOMETRY_CONSTRAINT = {}
    damping_factor = 0.5
    instances = set()

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

    def __init__(self, geometry, index, **kwargs):
        self._residual = None
        self._tangent = None
        self._normal = None
        self._geometry = geometry
        self._index = index
        if 'location' in kwargs:
            self._location = Point(*kwargs['location'])
            self.project_to_geometry()
        Constraint.instances.add(self)

    @property
    def geometry(self):
        return self._geometry

    @property
    def element_index(self):
        return self._index

    @property
    def location(self):
        return getattr(self, '_location', None)

    @property
    def residual(self):
        return self._residual

    @residual.setter
    def residual(self, residual):
        self._tangent = None
        self._normal = None
        self._residual = residual

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

    def compute_tangent(self):
        raise NotImplementedError

    def compute_normal(self):
        raise NotImplementedError

    def project_to_geometry(self):
        raise NotImplementedError

    def update_location(self):
        self._location += self.tangent * Constraint.damping_factor

    # replace with vectorized function collecting all tangent residuals
    @classmethod
    def update_vertices(cls, result, constraints=None):
        """Update the coordinates of all constrained vertices."""
        vertices = result.vertices.copy()
        constraints = constraints or cls.instances
        for constraint in constraints:
            index = constraint.element_index
            if constraint.location is None:
                constraint._location = result.vertices[index]
            constraint.residual = result.residuals[index]
            constraint.update_location()
            vertices[index] = constraint.location
        return vertices
