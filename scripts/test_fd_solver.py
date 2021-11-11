import compas
from compas.geometry import Point, Line, Vector
from compas_fd.datastructures import CableMesh

from compas_fd.numdata import FDNumericalData
from compas_fd.solvers import FDSolver

from compas_view2.app import App
from compas_view2.objects import Object, MeshObject

Object.register(CableMesh, MeshObject)

mesh = CableMesh.from_obj(compas.get('faces.obj'))

mesh.vertices_attribute('is_anchor', True, keys=list(mesh.vertices_where({'vertex_degree': 2})))
mesh.vertices_attribute('t', 0.0)

# input parameters
vertex_index = mesh.vertex_index()
vertices = mesh.vertices_attributes('xyz')
fixed = list(mesh.vertices_where({'is_anchor': True}))
edges = [(vertex_index[u], vertex_index[v]) for
         u, v in mesh.edges_where({'_is_edge': True})]
forcedensities = mesh.edges_attribute('q')
loads = mesh.vertices_attributes(['px', 'py', 'pz'])

# set up single iteration solver
numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)
solver = FDSolver(numdata)

# run solver
result = solver()

# update mesh
for index, vertex in enumerate(mesh.vertices()):
    mesh.vertex_attributes(vertex, 'xyz', result.vertices[index])
    mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz'], result.residuals[index])


# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

viewer.add(mesh)

for vertex in fixed:
    viewer.add(Point(* mesh.vertex_attributes(vertex, 'xyz')), size=20, color=(0, 0, 0))

for vertex in fixed:
    a = Point(* mesh.vertex_attributes(vertex, 'xyz'))
    b = a - Vector(* mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz']))
    viewer.add(Line(a, b), linewidth=3, linecolor=(0, 0, 1))

viewer.run()
