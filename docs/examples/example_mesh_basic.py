from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Vector
from compas_fd.solvers import fd_numpy
from compas_viewer import Viewer

mesh = Mesh.from_meshgrid(dx=10, nx=10)

vertices = mesh.vertices_attributes("xyz")
fixed = list(mesh.vertices_where(vertex_degree=2))
edges = list(mesh.edges())
loads = [[0, 0, 0] for _ in range(len(vertices))]

q = []
for edge in edges:
    if mesh.is_edge_on_boundary(edge):
        q.append(10)
    else:
        q.append(1.0)

result = fd_numpy(
    vertices=vertices,
    fixed=fixed,
    edges=edges,
    forcedensities=q,
    loads=loads,
)

for vertex, attr in mesh.vertices(data=True):
    attr["x"] = result.vertices[vertex, 0]
    attr["y"] = result.vertices[vertex, 1]
    attr["z"] = result.vertices[vertex, 2]

viewer = Viewer()
viewer.renderer.camera.target = [5, 5, 0]
viewer.renderer.camera.position = [5, -5, 20]

viewer.scene.add(mesh, show_points=False)

for vertex in fixed:
    point = Point(*mesh.vertex_coordinates(vertex))
    residual = Vector(*result.residuals[vertex])
    ball = Sphere(radius=0.1, point=point)

    viewer.scene.add(ball.to_brep(), surfacecolor=Color.red(), show_points=False)
    viewer.scene.add(
        Line(point, point - residual * 0.1),
        linecolor=Color.green().darkened(50),
        lineswidth=3,
        show_points=False,
    )

viewer.show()
