from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Line

from .constraint import Constraint
from .lineconstraint import LineConstraint

Constraint.GEOMETRY_CONSTRAINT[Line] = LineConstraint
