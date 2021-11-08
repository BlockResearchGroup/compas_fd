from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface

from .constraint import Constraint
from .lineconstraint import LineConstraint
from .planeconstraint import PlaneConstraint
from .curveconstraint import CurveConstraint
from .surfaceconstraint import SurfaceConstraint

Constraint.GEOMETRY_CONSTRAINT[Line] = LineConstraint
Constraint.GEOMETRY_CONSTRAINT[Plane] = PlaneConstraint
Constraint.GEOMETRY_CONSTRAINT[NurbsCurve] = CurveConstraint
Constraint.GEOMETRY_CONSTRAINT[NurbsSurface] = SurfaceConstraint
