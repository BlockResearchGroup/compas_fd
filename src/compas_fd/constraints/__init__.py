"""
***************************
constraints
***************************

.. currentmodule:: compas_fd.constraints

Base Class
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Constraint

Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    CircleConstraint
    CurveConstraint
    FrameConstraint
    LineConstraint
    PlaneConstraint
    SurfaceConstraint
    VectorConstraint

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface

from .constraint import Constraint

from .vectorconstraint import VectorConstraint
from .frameconstraint import FrameConstraint
from .lineconstraint import LineConstraint
from .planeconstraint import PlaneConstraint
from .circleconstraint import CircleConstraint

from .curveconstraint import CurveConstraint
from .surfaceconstraint import SurfaceConstraint

Constraint.register(Vector, VectorConstraint)
Constraint.register(Frame, FrameConstraint)
Constraint.register(Line, LineConstraint)
Constraint.register(Plane, PlaneConstraint)
Constraint.register(Circle, CircleConstraint)

Constraint.register(NurbsCurve, CurveConstraint)
Constraint.register(NurbsSurface, SurfaceConstraint)
