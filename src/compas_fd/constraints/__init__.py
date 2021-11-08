from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCNurbsSurface

from .constraint import Constraint
from .lineconstraint import LineConstraint
from .planeconstraint import PlaneConstraint
from .curveconstraint import CurveConstraint
from .surfaceconstraint import SurfaceConstraint

Constraint.register(Line, LineConstraint)
Constraint.register(Plane, PlaneConstraint)
Constraint.register(NurbsCurve, CurveConstraint)
Constraint.register(OCCNurbsCurve, CurveConstraint)
Constraint.register(NurbsSurface, SurfaceConstraint)
Constraint.register(OCCNurbsSurface, SurfaceConstraint)
