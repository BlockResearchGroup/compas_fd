from compas_view2.app import App
from compas.datastructures import Mesh
from compas_fd.solvers import fd_numpy

mesh = Mesh.from_meshgrid(dx=10, nx=10)

bottomleft = list(mesh.vertices_where(x=0, y=0))[0]
topright = list(mesh.vertices_where(x=10, y=10))[0]

# bottomleft = mesh.vertex_where(x=0, y=0)
# topright = mesh.vertex_where(x=10, y=10)

mesh.vertices_attribute(name="z", value=7, keys=[bottomleft, topright])

# mesh.vertices[bottomleft]['z'] = 7.0
# mesh.vertices[topright]['z'] = 7.0

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

viewer = App()
viewer.add(mesh)
viewer.view.camera.zoom_extents()
viewer.run()
