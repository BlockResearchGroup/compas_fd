from __future__ import annotations

import inspect
from collections.abc import Iterable
from typing import Any
from typing import ClassVar
from typing import Self
from typing import cast

from compas.data import Data
from compas.geometry import Point
from compas.geometry import Vector
from compas.linalg import vector_component

from .exceptions import GeometryNotRegisteredAsConstraint


class Constraint[GeometryT: Data](Data):
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

    GEOMETRY_CONSTRAINT: ClassVar[dict[type[Data], type[Constraint[Any]]]] = {}

    @staticmethod
    def register(gtype: type[Data], ctype: type[Constraint[Any]]) -> None:
        Constraint.GEOMETRY_CONSTRAINT[gtype] = ctype

    @staticmethod
    def get_constraint_cls(geometry: Data, **kwargs: object) -> type[Constraint[Any]]:
        gtype = type(geometry)
        cls = None
        for type_ in inspect.getmro(gtype):
            cls = Constraint.GEOMETRY_CONSTRAINT.get(type_)
            if cls is not None:
                break
        if cls is None:
            raise GeometryNotRegisteredAsConstraint("No constraint is registered for this geometry type: {}".format(gtype))
        return cls

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        geometry = args[0]
        target = Constraint.get_constraint_cls(geometry)
        return cast(Self, super(Constraint, target).__new__(target))

    @property
    def __data__(self) -> dict[str, Any]:
        data: dict[str, Any] = {"geometry": self.geometry.__data__}
        if self._rhino_guid:
            data["rhino_guid"] = str(self._rhino_guid)
        return data

    def __init__(self, geometry: GeometryT, name: str | None = None) -> None:
        super(Constraint, self).__init__(name=name)
        self._geometry: GeometryT
        self._location: Point | None = None
        self._residual: Vector | None = None
        self._tangent: Vector | None = None
        self._normal: Vector | None = None
        self._rhino_guid: str | None = None
        self._param: float | tuple[float, float] | None = None
        self.geometry = geometry

    def __repr__(self) -> str:
        return "{}({}, name={})".format(self.__class__.__name__, repr(self.geometry), self._name)

    # =============================================================================
    # Managed attributes
    # =============================================================================

    @property
    def geometry(self) -> GeometryT:
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: GeometryT) -> None:
        self._residual = None
        self._tangent = None
        self._normal = None
        self._geometry = geometry

    @property
    def location(self) -> Point | None:
        return self._location

    @location.setter
    def location(self, point: Iterable[float]) -> None:
        self._tangent = None
        self._normal = None
        self._location = Point(*cast("tuple[float, float, float]", point))
        if not getattr(self, "projected", None):
            self.project()
            self.projected = True

    @property
    def residual(self) -> Vector | None:
        return self._residual

    @residual.setter
    def residual(self, residual: Iterable[float]) -> None:
        self._tangent = None
        self._normal = None
        self._residual = Vector(*cast("tuple[float, float, float]", residual))

    @property
    def tangent(self) -> Vector:
        if self._tangent is None:
            self.compute_tangent()
        return cast(Vector, self._tangent)

    @property
    def normal(self) -> Vector:
        if self._normal is None:
            self.compute_normal()
        return cast(Vector, self._normal)

    @property
    def param(self) -> float | tuple[float, float] | None:
        if self._param is None:
            self.compute_param()
        return self._param

    # =============================================================================
    # "Abstract" methods
    # =============================================================================

    def _project_residual(self, direction: Vector) -> Vector:
        """Project the current residual onto a tangent or normal direction."""
        # COMPAS accepts vector-like objects here. Its type declaration uses Sequence.
        x, y, z = vector_component(tuple(cast(Vector, self.residual)), tuple(direction))
        return Vector(x, y, z)

    def compute_tangent(self) -> None:
        raise NotImplementedError

    def compute_normal(self) -> None:
        raise NotImplementedError

    def update(self, damping: float = 0.1) -> None:
        raise NotImplementedError

    def compute_param(self) -> None:
        raise NotImplementedError

    def project(self) -> None:
        raise NotImplementedError

    def update_location_at_param(self) -> None:
        raise NotImplementedError
