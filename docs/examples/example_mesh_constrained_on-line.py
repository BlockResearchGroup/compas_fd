from compas_view2.app import App
from compas.datastructures import Mesh
from compas.geometry import Point, Vector, Line, Sphere
from compas.colors import Color
from compas_fd.solvers import fd_constrained_numpy
from compas_fd.constraints import Constraint

# set up the mesh

mesh = Mesh.from_meshgrid(dx=10, nx=10)

# vertices, edges, loads, and fixed vertices

vertices = mesh.vertices_attributes("xyz")
fixed = list(mesh.vertices_where(vertex_degree=2))
edges = list(mesh.edges())
loads = [[0, 0, 0] for _ in range(len(vertices))]

centervertex = list(mesh.vertices_where(x=5, y=5))[0]
loads[centervertex][2] = -3

# force densities

q = []
for edge in edges:
    if mesh.is_edge_on_boundary(edge):
        q.append(10)
    else:
        q.append(1.0)

# constraints

constraints = [None] * len(vertices)
vertex = list(mesh.vertices_where(x=0, y=10))[0]
line = Line([-1, 2, 0], [0, 10, 0])
constraint = Constraint(line)
constraints[vertex] = constraint

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
    load = Vector(*loads[vertex])
    residual = Vector(*result.residuals[vertex])

    if vertex in fixed:
        constraint = constraints[vertex]
        ball = Sphere(radius=0.05, point=point)

        if constraint:
            viewer.add(ball.to_brep(), facecolor=Color.blue())
            viewer.add(constraint.geometry, linecolor=Color.cyan(), linewidth=3)
        else:
            viewer.add(ball.to_brep(), facecolor=Color.red())

        viewer.add(
            Line(point, point - residual * 0.1),
            linecolor=Color.green().darkened(50),
            linewidth=3,
        )

    if load.length > 0:
        viewer.add(
            Line(point, point + load * 0.1),
            linecolor=Color.green().darkened(50),
            linewidth=3,
        )


viewer.view.camera.zoom_extents()
viewer.run()
