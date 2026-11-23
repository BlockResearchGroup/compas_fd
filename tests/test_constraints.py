import numpy as np
import pytest
from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Vector

from compas_fd.constraints import Constraint
from compas_fd.constraints import LineConstraint
from compas_fd.constraints import SurfaceConstraint
from compas_fd.solvers import fd_constrained_numpy


def test_constrained_hypar_projects_free_vertex_to_line():
    constraint = Constraint(Line([0, 0, 0], [1, 0, 0]))
    result = fd_constrained_numpy(
        vertices=[[0, 0, 0], [0, 0, 1], [1, 0, 0], [1, 1, 1], [0, 1, 0]],
        fixed=[1, 2, 3, 4],
        edges=[(0, 1), (0, 2), (0, 3), (0, 4)],
        forcedensities=[1, 1, 1, 1],
        constraints=[constraint, None, None, None, None],
        kmax=100,
        tol_res=1e-9,
        tol_disp=1e-9,
        damping=1.0,
    )

    np.testing.assert_allclose(result.vertices[0], [0.5, 0.0, 0.0], rtol=0, atol=1e-12)
    # The 0.5.4 baseline reports the residual from the solve before projection.
    assert result.residuals is not None
    np.testing.assert_allclose(result.residuals[0], [0.0, 0.0, 0.0], rtol=0, atol=1e-12)


def test_line_constraint_projects_location_and_decomposes_residual():
    constraint = Constraint(Line([0, 0, 0], [1, 0, 0]))
    constraint.location = [0.5, 1.0, 1.0]
    constraint.residual = [1.0, 2.0, 3.0]

    location = constraint.location
    assert location is not None
    np.testing.assert_allclose(tuple(location), [0.5, 0.0, 0.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(tuple(constraint.tangent), [1.0, 0.0, 0.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(tuple(constraint.normal), [0.0, 2.0, 3.0], rtol=0, atol=1e-12)


def test_constrained_support_slides_to_equilibrium():
    constraint = LineConstraint(Line([0, 0, 0], [3, 0, 0]))
    result = fd_constrained_numpy(
        vertices=[[0, 0, 0], [2, 1, 0], [1, 0, 0]],
        fixed=[0, 1],
        edges=[(0, 2), (1, 2)],
        forcedensities=[1, 1],
        constraints=[constraint, None, None],
        kmax=100,
        tol_res=1e-9,
        damping=1.0,
    )

    # The free vertex is the midpoint of the supports. Zero tangential
    # residual puts the sliding support directly below the fixed one.
    np.testing.assert_allclose(result.vertices, [[2, 0, 0], [2, 1, 0], [2, 0.5, 0]], rtol=0, atol=1e-9)
    np.testing.assert_allclose(tuple(constraint.normal), [0, 0.5, 0], rtol=0, atol=1e-12)


def test_line_constraint_loads_compas2_json():
    serialized = (
        '{"dtype":"compas_fd.constraints/LineConstraint",'
        '"data":{"geometry":{"start":[0.0,0.0,0.0],"end":[1.0,0.0,0.0]}},'
        '"guid":"51e745e5-611a-4377-8f39-0125373d55de","name":"support"}'
    )
    constraint = LineConstraint.from_jsonstring(serialized)

    assert isinstance(constraint, LineConstraint)
    assert constraint.__data__ == {"geometry": {"start": [0.0, 0.0, 0.0], "end": [1.0, 0.0, 0.0]}}
    assert constraint.name == "support"
    assert str(constraint.guid) == "51e745e5-611a-4377-8f39-0125373d55de"
    assert LineConstraint.from_jsonstring(constraint.to_jsonstring()).__data__ == constraint.__data__


def test_nurbs_surface_constraint_retains_legacy_payload_and_projects(monkeypatch: pytest.MonkeyPatch) -> None:
    from compas.geometry.surfaces import nurbs

    control_points = [[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]], [[0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]]

    class TestSurface(NurbsSurface):
        @property
        def __data__(self) -> dict[str, object]:
            return {"control_points": control_points}

    def load_surface(cls: type[NurbsSurface], data: dict[str, object]) -> NurbsSurface:
        assert data == {"control_points": control_points}
        return TestSurface()

    def closest_point(_surface: NurbsSurface, _point: Point, *, return_parameters: bool) -> Point | tuple[Point, tuple[float, float]]:
        point = Point(0.5, 0.5, 0.0)
        return (point, (0.5, 0.5)) if return_parameters else point

    def normal_at(_surface: NurbsSurface, _u: float, _v: float) -> Vector:
        return Vector(0.0, 0.0, 1.0)

    monkeypatch.setattr(NurbsSurface, "__from_data__", classmethod(load_surface))
    monkeypatch.setattr(nurbs, "surface_closest_point", closest_point)
    monkeypatch.setattr(nurbs, "surface_normal_at", normal_at)
    legacy = {"geometry": {"points": control_points}, "rhino_guid": "support"}
    constraint = SurfaceConstraint.__from_data__(legacy)
    constraint.location = [0.5, 0.5, 1.0]
    constraint.residual = [1.0, 2.0, 3.0]

    assert constraint.__data__ == legacy
    assert legacy["geometry"] == {"points": control_points}
    assert constraint.location == Point(0.5, 0.5, 0.0)
    assert constraint.tangent == Vector(1.0, 2.0, 0.0)
    assert constraint.normal == Vector(0.0, 0.0, 3.0)
