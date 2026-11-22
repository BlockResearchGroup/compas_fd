import json
import math
import pathlib

import compas
import pytest
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Vector

from compas_fd.constraints import CircleConstraint
from compas_fd.constraints import Constraint
from compas_fd.constraints import CurveConstraint
from compas_fd.constraints import FrameConstraint
from compas_fd.constraints import LineConstraint
from compas_fd.constraints import PlaneConstraint
from compas_fd.constraints import SurfaceConstraint
from compas_fd.constraints import VectorConstraint

COMPAS2_JSON = pathlib.Path(__file__).parent / "baselines" / "constraints.json"

RHINO_GUID = "7a1b3c5d-0000-4000-8000-123456789abc"

COMPAS2_DATA = [
    (LineConstraint, {"geometry": {"start": [5.0, -1.0, 0.0], "end": [5.0, 11.0, 0.0]}}),
    (PlaneConstraint, {"geometry": {"point": [5.0, 0.0, 0.0], "normal": [1.0, 0.0, 0.0]}, "rhino_guid": RHINO_GUID}),
    (VectorConstraint, {"geometry": [0.0, 1.0, 0.0]}),
    (FrameConstraint, {"geometry": {"point": [5.0, 0.0, 0.0], "xaxis": [0.0, 1.0, 0.0], "yaxis": [0.0, 0.0, 1.0]}}),
]


# =============================================================================
# Registration and dispatch
# =============================================================================


@pytest.mark.parametrize(
    ("geometry", "ctype"),
    [
        (Vector(0, 1, 0), VectorConstraint),
        (Frame([5, 0, 0], [0, 1, 0], [0, 0, 1]), FrameConstraint),
        (Line([5, -1, 0], [5, 11, 0]), LineConstraint),
        (Plane([5, 0, 0], [1, 0, 0]), PlaneConstraint),
        (Circle(2.0), CircleConstraint),
    ],
)
def test_dispatch(geometry, ctype):
    constraint = Constraint(geometry)
    assert type(constraint) is ctype
    assert constraint.geometry is geometry


def test_nurbs_geometry_is_registered():
    assert Constraint.GEOMETRY_CONSTRAINT[NurbsCurve] is CurveConstraint
    assert Constraint.GEOMETRY_CONSTRAINT[NurbsSurface] is SurfaceConstraint


@pytest.mark.parametrize(
    "ctype",
    [Constraint, VectorConstraint, FrameConstraint, LineConstraint, PlaneConstraint, CircleConstraint, CurveConstraint, SurfaceConstraint],
)
def test_no_dataschema(ctype):
    assert not hasattr(ctype, "DATASCHEMA")


# =============================================================================
# Data
# =============================================================================


def test_compas2_json_loads():
    constraints = compas.json_loads(COMPAS2_JSON.read_text(encoding="utf-8"))

    assert [(type(constraint), constraint.__data__) for constraint in constraints] == COMPAS2_DATA
    assert [constraint._rhino_guid for constraint in constraints] == [None, RHINO_GUID, None, None]


def test_compas2_json_roundtrip():
    text = COMPAS2_JSON.read_text(encoding="utf-8")
    dumped = compas.json_dumps(compas.json_loads(text))

    # the serialised form is unchanged
    old = [(item["dtype"], item["data"]) for item in json.loads(text)]
    new = [(item["dtype"], item["data"]) for item in json.loads(dumped)]
    assert new == old

    constraints = compas.json_loads(dumped)

    assert [(type(constraint), constraint.__data__) for constraint in constraints] == COMPAS2_DATA
    assert constraints[1]._rhino_guid == RHINO_GUID


# =============================================================================
# CircleConstraint on a Circle (closed form; no COMPAS 2 baseline exists)
# =============================================================================


def test_circle_constraint_closed_form():
    # circle of radius 2 around (1, 2, 3) in the plane spanned by e1 = Y and e2 = Z (normal X)
    radius = 2.0
    center = Vector(1.0, 2.0, 3.0)
    e1 = Vector(0.0, 1.0, 0.0)
    e2 = Vector(0.0, 0.0, 1.0)
    e3 = Vector(1.0, 0.0, 0.0)
    circle = Circle(radius, frame=Frame(Point(*center), e1, e2))

    # a point at 45 degrees, outside the circle and out of its plane
    angle = math.pi / 4
    radial = e1 * math.cos(angle) + e2 * math.sin(angle)
    direction = e1 * -math.sin(angle) + e2 * math.cos(angle)

    constraint = Constraint(circle)
    constraint.location = center + radial * 3.0 + e3 * 0.7

    assert type(constraint) is CircleConstraint
    assert list(constraint.location) == pytest.approx(list(center + radial * radius), abs=1e-12)
    assert constraint.param == pytest.approx(0.125, abs=1e-12)

    residual = Vector(1.0, 2.0, 3.0)
    tangent = direction * residual.dot(direction)
    normal = residual - tangent

    constraint.residual = residual

    assert list(constraint.tangent) == pytest.approx(list(tangent), abs=1e-12)
    assert list(constraint.normal) == pytest.approx(list(normal), abs=1e-12)

    # the update moves along the tangent and pulls the point back onto the circle
    damping = 0.1
    moved = radial * radius + tangent * damping
    expected = center + moved * (radius / moved.length)

    constraint.update(damping=damping)

    assert list(constraint.location) == pytest.approx(list(expected), abs=1e-12)
    assert constraint.param == pytest.approx(math.atan2(moved.dot(e2), moved.dot(e1)) / (2 * math.pi), abs=1e-12)


# =============================================================================
# SurfaceConstraint (closed form; needs a NURBS backend; never ran on COMPAS 2)
# =============================================================================


def test_surface_constraint_normal_closed_form():
    pytest.importorskip("compas_occ")

    # Bezier surface of degree 2 x 2 that is exactly z = x**2 for x in [-1, 1] and y in [0, 2]
    points = [[[x, y, z] for y in (0.0, 1.0, 2.0)] for x, z in ((-1.0, 1.0), (0.0, -1.0), (1.0, 1.0))]
    surface = NurbsSurface.from_points(points, degree_u=2, degree_v=2)

    # at x = 0.5 the unit normal of z = x**2 is (-2x, 0, 1) / sqrt(1 + 4x**2) = (-1, 0, 1) / sqrt(2), up to its sign
    foot = Point(0.5, 0.5, 0.25)
    unit_normal = Vector(-1.0, 0.0, 1.0) * (1 / math.sqrt(2))

    constraint = Constraint(surface)
    constraint.location = foot + unit_normal * 0.3

    assert type(constraint) is SurfaceConstraint
    assert list(constraint.location) == pytest.approx(list(foot), abs=1e-6)

    # the normal component of the residual does not depend on the sign of the surface normal
    residual = Vector(1.0, 2.0, 3.0)
    normal = unit_normal * residual.dot(unit_normal)
    tangent = residual - normal

    constraint.residual = residual

    assert list(constraint.normal) == pytest.approx(list(normal), abs=1e-6)
    assert list(constraint.tangent) == pytest.approx(list(tangent), abs=1e-6)
