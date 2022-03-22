from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import Vector
from .constraint import Constraint


class VectorConstraint(Constraint):

    def __init__(self, vector, **kwargs):
        super(VectorConstraint, self).__init__(geometry=vector, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data}

    @data.setter
    def data(self, data):
        self.geometry = Vector.from_data(data['geometry'])

    @classmethod
    def from_data(cls, data):
        vector = Vector.from_data(data['geometry']).unitized()
        return cls(vector)

    def compute_tangent(self):
        self._tangent = Vector(* vector_component(self.residual, self.geometry))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def update(self, damping=0.1):
        self._location = self.location + self.tangent * damping

    def project(self):
        pass
