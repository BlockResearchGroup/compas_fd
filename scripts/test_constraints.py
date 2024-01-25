from functools import partial
import compas
from compas.geometry import Vector, Point, Line
from compas_fd.datastructures import CableMesh
from compas_fd.solvers import fd_numpy

from compas_fd.constraints import Constraint

from compas_view2.app import App
from compas_view2.objects import Object, MeshObject

Object.register(CableMesh, MeshObject)

mesh = CableMesh.from_obj(compas.get("faces.obj"))

mesh.vertices_attribute(
    "is_anchor", True, keys=list(mesh.vertices_where({"vertex_degree": 2}))
)
mesh.vertices_attribute("t", 0.0)

vertex = list(mesh.vertices_where({"x": 10, "y": 10}))[0]
line = Line(Point(10, 0, 0), Point(14, 10, 0))
constraint = Constraint(line)

mesh.vertex_attribute(vertex, "constraint", constraint)

vertex_index = mesh.vertex_index()

vertices = mesh.vertices_attributes("xyz")
edges = [
    (vertex_index[u], vertex_index[v]) for u, v in mesh.edges_where({"_is_edge": True})
]
loads = mesh.vertices_attributes(["px", "py", "pz"])
forcedensities = mesh.edges_attribute("q")
fixed = list(mesh.vertices_where({"is_anchor": True}))
constraints = mesh.vertices_attribute("constraint", keys=fixed)

fd = partial(
    fd_numpy, edges=edges, loads=loads, forcedensities=forcedensities, fixed=fixed
)

for k in range(100):
    result = fd(vertices=vertices)
    residuals = result.residuals
    vertices = result.vertices
    for vertex, constraint in zip(fixed, constraints):
        if not constraint:
            continue
        constraint.location = vertices[vertex]
        constraint.residual = residuals[vertex]
        vertices[vertex] = constraint.location + constraint.tangent * 0.5

for index, vertex in enumerate(mesh.vertices()):
    mesh.vertex_attributes(vertex, "xyz", vertices[index])
    mesh.vertex_attributes(vertex, ["_rx", "_ry", "_rz"], residuals[index])

# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

viewer.add(mesh)

for vertex in fixed:
    viewer.add(Point(*mesh.vertex_attributes(vertex, "xyz")), size=20, color=(0, 0, 0))

for constraint in constraints:
    if constraint:
        viewer.add(constraint.geometry, linewidth=5, linecolor=(0, 1, 1))

for vertex in fixed:
    a = Point(*mesh.vertex_attributes(vertex, "xyz"))
    b = a - Vector(*mesh.vertex_attributes(vertex, ["_rx", "_ry", "_rz"]))
    viewer.add(Line(a, b), linewidth=3, linecolor=(0, 0, 1))

viewer.run()
