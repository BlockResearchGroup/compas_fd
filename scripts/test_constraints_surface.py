import compas
from compas.geometry import Vector, Point, Line
from compas_fd.datastructures import CableMesh

from compas.geometry import NurbsSurface

from compas_fd.constraints import Constraint
from compas_fd.fd import mesh_fd_constraint_numpy

from compas_view2.app import App
from compas_view2.objects import Object, MeshObject

Object.register(CableMesh, MeshObject)

mesh = CableMesh.from_obj(compas.get('faces.obj'))

mesh.vertices_attribute('is_anchor', True, keys=list(mesh.vertices_where({'vertex_degree': 2})))
mesh.vertices_attribute('t', 0.0)

# surface constraint
vertex = list(mesh.vertices_where({'x': 10, 'y': 10}))[0]
points = [
    [Point(0, 0, 10), Point(3, 0, 10), Point(6, 0, 10), Point(9, 0, 10)],
    [Point(0, 3, 0), Point(3, 3, 6), Point(6, 3, 6), Point(9, 3, 0)],
    [Point(0, 6, 0), Point(3, 6, 6), Point(6, 6, 6), Point(9, 6, 0)],
    [Point(0, 9, 10), Point(3, 9, 10), Point(6, 9, 10), Point(9, 9, 10)],
]
surface = NurbsSurface.from_points(points=points)
constraint = Constraint(surface)
mesh.vertex_attribute(vertex, 'constraint', constraint)

fixed = list(mesh.vertices_where({'is_anchor': True}))
constraints = mesh.vertices_attribute('constraint')

# solve
mesh = mesh_fd_constraint_numpy(mesh)

# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

viewer.add(mesh)

for vertex in fixed:
    viewer.add(Point(* mesh.vertex_attributes(vertex, 'xyz')), size=20, color=(0, 0, 0))

for constraint in constraints:
    if constraint:
        viewer.add(surface.to_mesh(nu=10))

for vertex in fixed:
    a = Point(* mesh.vertex_attributes(vertex, 'xyz'))
    b = a - Vector(* mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz']))
    viewer.add(Line(a, b), linewidth=3, linecolor=(0, 0, 1))

viewer.run()
