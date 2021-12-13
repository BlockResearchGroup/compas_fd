from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import vector_component
from compas.geometry import project_point_line
from compas.geometry import Vector
from compas.geometry import Point
from compas.geometry import Line
from .constraint import Constraint

import compas
if compas.IPY:  # Tom: is this allowed?
    from compas_rhino.geometry import RhinoLine
    import Rhino


class LineConstraint(Constraint):

    def __init__(self, line, **kwargs):
        super(LineConstraint, self).__init__(geometry=line, **kwargs)

    @property
    def data(self):
        return {'geometry': self.geometry.data, 'guid': str(self.guid)}

    @data.setter
    def data(self, data):
        self.geometry = Line.from_data(data['geometry'])
        self.guid = data['guid']

    @classmethod
    def from_data(cls, data):
        line = Line.from_data(data['geometry'])
        constraint = cls(line)
        constraint.guid = data['guid']
        return constraint

    def compute_tangent(self):
        direction = self.geometry.direction
        self._tangent = Vector(*vector_component(self.residual, direction))

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project(self):
        self._location = Point(*project_point_line(self._location, self.geometry))

    def compute_param(self):
        v = Vector.from_start_end(self._geometry.start, self._location)
        u = self._geometry.vector
        d = v.dot(u)
        self._param = v.length * d/abs(d)

    def update_location_at_param(self):
        d = self._geometry.direction
        self._location = self._geometry.start + d * self._param

    def update_geometry_guid(self):
        self._geometry = RhinoLine.from_guid(self._guid).to_compas()

    def rhinogeometry(self):
        start = Rhino.Geometry.Point3d(self._geometry.start.x, self._geometry.start.y, self._geometry.start.z)
        end = Rhino.Geometry.Point3d(self._geometry.end.x, self._geometry.end.y, self._geometry.end.z)
        return Rhino.Geometry.Line(start, end)
