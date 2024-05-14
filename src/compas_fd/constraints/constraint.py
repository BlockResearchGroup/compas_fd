from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import inspect

from compas.data import Data
from compas.geometry import Point
from compas.geometry import Vector

from .exceptions import GeometryNotRegisteredAsConstraint


class Constraint(Data):
    """Base class for all constraints.

    Parameters
    ----------
    geometry : :class:`compas.geometry.Geometry`
        The geometry of the constraint.
    name : str, optional
        The name of the constraint.

    Attributes
    ----------
    geometry : :class:`compas.geometry.Geometry`
        The geometry of the constraint.
    location : :class:`compas.geometry.Point`
        The location of the constrained vertex.
    residual : :class:`compas.geometry.Vector`
        The residual vector at the constrained vertex.
    tangent : :class:`compas.geometry.Vector`
        The tangent vector of the residual at the constrained vertex.
    normal : :class:`compas.geometry.Vector`
        The normal vector of the residual at the constrained vertex.
    param : float
        The parameter of the closest point on the constraint geometry to the location of the constrained vertex.

    Notes
    -----
    The constraint class using a registration mechanism to
    determine the type of constraint object for a given constraint geometry.
    Therefore, this class is the main entry point for creating constraints.

    Examples
    --------
    >>> from compas.geometry import Line
    >>> from compas_fd.constraints import Constraint
    >>> line = Line([0, 0, 0], [1, 0, 0])
    >>> constraint = Constraint(line)
    >>> constraint
    LineConstraint(Line(Point(x=0.0, y=0.0, z=0.0), Point(x=1.0, y=0.0, z=0.0)), name=None)

    """

    GEOMETRY_CONSTRAINT = {}

    @staticmethod
    def register(gtype, ctype):
        Constraint.GEOMETRY_CONSTRAINT[gtype] = ctype

    @staticmethod
    def get_constraint_cls(geometry, **kwargs):
        gtype = type(geometry)
        cls = None
        for type_ in inspect.getmro(gtype):
            cls = Constraint.GEOMETRY_CONSTRAINT.get(type_)
            if cls is not None:
                break
        if cls is None:
            raise GeometryNotRegisteredAsConstraint("No constraint is registered for this geometry type: {}".format(gtype))
        return cls

    def __new__(cls, *args, **kwargs):
        geometry = args[0]
        cls = Constraint.get_constraint_cls(geometry)
        return super(Constraint, cls).__new__(cls)

    @property
    def __data__(self):
        data = {"geometry": self.geometry.__data__}
        if self._rhino_guid:
            data["rhino_guid"] = str(self._rhino_guid)
        return data

    def __init__(self, geometry, name=None):
        super(Constraint, self).__init__(name=name)
        self._geometry = None
        self._location = None
        self._residual = None
        self._tangent = None
        self._normal = None
        self._rhino_guid = None
        self._param = None
        self.geometry = geometry

    def __repr__(self):
        return "{}({}, name={})".format(self.__class__.__name__, repr(self.geometry), self._name)

    # =============================================================================
    # Managed attributes
    # =============================================================================

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
        if not getattr(self, "projected", None):
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

    # =============================================================================
    # "Abstract" methods
    # =============================================================================

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
