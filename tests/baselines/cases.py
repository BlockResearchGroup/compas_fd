"""Baseline cases of ``compas_fd`` (single definition of inputs and calls).

Used by ``record.py`` (COMPAS 2, legacy revision) and by ``tests/test_baselines.py``.
Only API that exists unchanged on COMPAS 2 and COMPAS 3 is used here.

Every numerical case is a function without arguments returning ``(inputs, outputs)``:
two dictionaries of NumPy arrays (``float64`` or ``int64``).
Inputs are rebuilt on every call; the solvers and the constraints are never reused between runs.

Shared input "grid": ``Mesh.from_meshgrid(dx=10, nx=10)`` (121 vertices, 220 edges),
the four corners fixed, force density 10 on boundary edges and 1 inside,
load (0, 0, -0.5) per vertex where stated.
"Column" is the eleven vertices at x = 5.
No random numbers are used.
"""

import compas
import numpy as np
from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Vector

from compas_fd.constraints import Constraint
from compas_fd.loads import SelfweightCalculator
from compas_fd.solvers import fd_constrained_numpy
from compas_fd.solvers import fd_numpy

LOAD = [0.0, 0.0, -0.5]

RHINO_GUID = "7a1b3c5d-0000-4000-8000-123456789abc"

CONSTRAINTS_FILE = "constraints.json"


# =============================================================================
# Inputs
# =============================================================================


def make_mesh():
    return Mesh.from_meshgrid(dx=10, nx=10)


def make_grid(load=True):
    """Solver input of the grid, as plain Python lists."""
    mesh = make_mesh()
    index = mesh.vertex_index()
    vertices = mesh.vertices_attributes("xyz")
    fixed = [index[vertex] for vertex in mesh.vertices_where(vertex_degree=2)]
    edges = [(index[u], index[v]) for u, v in mesh.edges()]
    forcedensities = []
    for u, v in mesh.edges():
        on_boundary = mesh.halfedge[u][v] is None or mesh.halfedge[v][u] is None
        forcedensities.append(10.0 if on_boundary else 1.0)
    loads = [list(LOAD) for _ in vertices] if load else None
    column = [index[vertex] for vertex in mesh.vertices() if mesh.vertex_attribute(vertex, "x") == 5.0]
    if (len(vertices), len(edges), len(fixed), len(column)) != (121, 220, 4, 11):
        raise RuntimeError("The grid is not the documented baseline input.")
    return mesh, vertices, fixed, edges, forcedensities, loads, column


def make_line():
    return Line([5, -1, 0], [5, 11, 0])


def make_plane():
    return Plane([5, 0, 0], [1, 0, 0])


def make_vector():
    return Vector(0, 1, 0)


def make_frame():
    return Frame([5, 0, 0], [0, 1, 0], [0, 0, 1])


def make_curve():
    from compas.geometry import NurbsCurve

    return NurbsCurve.from_points([[5, 0, 0], [5, 5, 3], [5, 10, 0]])


def _floats(values, shape):
    return np.asarray(values, dtype=np.float64).reshape(shape)


def _ints(values, shape):
    return np.asarray(values, dtype=np.int64).reshape(shape)


def _solver_inputs(vertices, fixed, edges, forcedensities, loads):
    inputs = {
        "vertices": _floats(vertices, (-1, 3)),
        "fixed": _ints(fixed, (-1,)),
        "edges": _ints(edges, (-1, 2)),
        "forcedensities": _floats(forcedensities, (-1,)),
    }
    if loads is not None:
        inputs["loads"] = _floats(loads, (-1, 3))
    return inputs


def _result_outputs(result):
    return {
        "vertices": _floats(result.vertices, (-1, 3)),
        "residuals": _floats(result.residuals, (-1, 3)),
        "forces": _floats(result.forces, (-1, 1)),
        "lengths": _floats(result.lengths, (-1, 1)),
    }


# =============================================================================
# fd_numpy
# =============================================================================


def _fd(load):
    _, vertices, fixed, edges, forcedensities, loads, _ = make_grid(load=load)
    inputs = _solver_inputs(vertices, fixed, edges, forcedensities, loads)
    result = fd_numpy(vertices=vertices, fixed=fixed, edges=edges, forcedensities=forcedensities, loads=loads)
    return inputs, _result_outputs(result)


def fd_01():
    """``fd_numpy`` on the grid, ``loads=None``."""
    return _fd(load=False)


def fd_02():
    """``fd_numpy`` on the grid with the load."""
    return _fd(load=True)


# =============================================================================
# SelfweightCalculator
# =============================================================================


def fd_03():
    """``SelfweightCalculator`` on the grid, t = 0.1, density 22, on the fd-02 geometry."""
    _, outputs = fd_02()
    xyz = outputs["vertices"]
    mesh = make_mesh()
    mesh.update_default_vertex_attributes(t=0.1)
    calculator = SelfweightCalculator(mesh, density=22)
    selfweight = calculator(xyz.copy())
    inputs = {
        "xyz": xyz,
        "thickness": _floats(0.1, ()),
        "density": _floats(22, ()),
    }
    outputs = {
        "F": _floats(calculator.F.toarray(), (mesh.number_of_faces(), mesh.number_of_vertices())),
        "selfweight": _floats(selfweight, (-1, 1)),
    }
    return inputs, outputs


# =============================================================================
# fd_constrained_numpy
# =============================================================================


def _fd_constrained(make_geometry, selfweight_density=None, with_params=False, **options):
    """``fd_constrained_numpy`` on the loaded grid with the column also fixed,
    and every column vertex constrained by its own constraint on its own geometry."""
    mesh, vertices, fixed, edges, forcedensities, loads, column = make_grid(load=True)
    fixed = fixed + column
    constraints = [None] * len(vertices)
    for vertex in column:
        constraints[vertex] = Constraint(make_geometry())

    inputs = _solver_inputs(vertices, fixed, edges, forcedensities, loads)
    inputs["column"] = _ints(column, (-1,))
    for name, value in options.items():
        inputs[name] = _ints(value, ()) if isinstance(value, int) else _floats(value, ())

    selfweight = None
    if selfweight_density is not None:
        mesh.update_default_vertex_attributes(t=0.1)
        selfweight = SelfweightCalculator(mesh, density=selfweight_density)
        inputs["thickness"] = _floats(0.1, ())
        inputs["density"] = _floats(selfweight_density, ())

    result = fd_constrained_numpy(
        vertices=vertices,
        fixed=fixed,
        edges=edges,
        forcedensities=forcedensities,
        loads=loads,
        constraints=constraints,
        selfweight=selfweight,
        **options,
    )

    outputs = _result_outputs(result)
    outputs["constraint_locations"] = _floats([list(constraints[vertex].location) for vertex in column], (-1, 3))
    if with_params:
        outputs["constraint_params"] = _floats([constraints[vertex].param for vertex in column], (-1,))
    return inputs, outputs


def fd_04():
    """Column on a ``Line``; ``kmax=10``, ``tol_res=0.0``."""
    return _fd_constrained(make_line, kmax=10, tol_res=0.0)


def fd_05():
    """Column on a ``Plane``; ``kmax=10``, ``tol_res=0.0``."""
    return _fd_constrained(make_plane, kmax=10, tol_res=0.0)


def fd_06():
    """Column on a ``Vector``; ``kmax=10``, ``tol_res=0.0``."""
    return _fd_constrained(make_vector, kmax=10, tol_res=0.0)


def fd_07():
    """Column on a ``Frame``; ``kmax=10``, ``tol_res=0.0``."""
    return _fd_constrained(make_frame, kmax=10, tol_res=0.0)


def fd_08():
    """fd-05 with a ``SelfweightCalculator``, t = 0.1, density 1.0."""
    return _fd_constrained(make_plane, selfweight_density=1.0, kmax=10, tol_res=0.0)


def fd_09():
    """fd-05 stopping early: ``tol_res=0.1``, default ``kmax``."""
    return _fd_constrained(make_plane, tol_res=0.1)


def fd_11():
    """Column on a ``NurbsCurve`` (needs ``compas_occ``); ``kmax=10``, ``tol_res=0.0``."""
    return _fd_constrained(make_curve, with_params=True, kmax=10, tol_res=0.0)


CASES = {
    "fd-01": fd_01,
    "fd-02": fd_02,
    "fd-03": fd_03,
    "fd-04": fd_04,
    "fd-05": fd_05,
    "fd-06": fd_06,
    "fd-07": fd_07,
    "fd-08": fd_08,
    "fd-09": fd_09,
    "fd-11": fd_11,
}

# Cases that need an optional backend package.
BACKENDS = {"fd-11": "compas_occ"}


# =============================================================================
# Constraint data (fd-10)
# =============================================================================


def fd_10_constraints():
    """The four constraints of fd-10; the plane constraint carries a ``rhino_guid``."""
    constraints = [Constraint(make_line()), Constraint(make_plane()), Constraint(make_vector()), Constraint(make_frame())]
    constraints[1]._rhino_guid = RHINO_GUID
    return constraints


def fd_10():
    """``json_dumps`` of the four constraints (the COMPAS guids in the text are random)."""
    return compas.json_dumps(fd_10_constraints())
