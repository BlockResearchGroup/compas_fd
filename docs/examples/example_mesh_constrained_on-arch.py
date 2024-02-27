from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Vector
from compas_fd.constraints import Constraint
from compas_fd.solvers import fd_constrained_numpy
from compas_view2.app import App

# mesh

mesh = Mesh.from_meshgrid(dx=10, nx=10)

# vertices, edges

vertices = mesh.vertices_attributes("xyz")
edges = list(mesh.edges())

# fixed vertices

fixed = list(mesh.vertices_where(vertex_degree=2))

# loads

loads = [[0, 0, 0] for _ in range(mesh.number_of_vertices())]

# force densities

q = []
for edge in edges:
    if mesh.is_edge_on_boundary(edge):
        q.append(10)
    else:
        q.append(1.0)

# constraints

arch = NurbsCurve.from_points([[5, 0, 0], [5, 5, 5], [5, 10, 0]])
constraint = Constraint(arch)

constraints = [None] * mesh.number_of_vertices()
for vertex in mesh.vertices_where(x=5):
    constraints[vertex] = constraint
    fixed.append(vertex)

# =============================================================================
# Solve and Update
# =============================================================================

result = fd_constrained_numpy(
    vertices=vertices,
    fixed=fixed,
    edges=edges,
    forcedensities=q,
    loads=loads,
    constraints=constraints,
)

for vertex, attr in mesh.vertices(data=True):
    attr["x"] = result.vertices[vertex, 0]
    attr["y"] = result.vertices[vertex, 1]
    attr["z"] = result.vertices[vertex, 2]

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.add(mesh)

for vertex in mesh.vertices():
    point = Point(*mesh.vertex_coordinates(vertex))
    residual = Vector(*result.residuals[vertex])

    if vertex in fixed:
        ball = Sphere(radius=0.1, point=point)

        if constraints[vertex]:
            viewer.add(ball.to_brep(), facecolor=Color.blue())
        else:
            viewer.add(ball.to_brep(), facecolor=Color.red())

        viewer.add(
            Line(point, point - residual * 0.1),
            linecolor=Color.green().darkened(50),
            linewidth=3,
        )

viewer.add(arch.to_polyline(), linecolor=Color.cyan(), linewidth=3)

viewer.view.camera.zoom_extents()
viewer.run()
