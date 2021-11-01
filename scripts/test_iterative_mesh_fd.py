import compas
from compas.geometry import Vector, Point, Line, Plane, Polyline
from compas_nurbs import Curve
from compas_fd.datastructures import CableMesh

from compas_fd.constraints import Constraint, CurveConstraint

from compas_view2.app import App
from compas_view2.objects import Object, MeshObject

Object.register(CableMesh, MeshObject)


# set mesh
mesh = CableMesh.from_obj(compas.get('faces.obj'))
fixed = list(mesh.vertices_where({'vertex_degree': 2}))
mesh.vertices_attribute('is_anchor', True, keys=fixed)
vertex_index = mesh.vertex_index()

ma = {'density': 24.0, 'point_lc': 1, 'weight_lc': 1,
      'wind_lc': 0, 'snow_lc': 0}
dva = {'px': .0, 'py': .0, 'pz': -.1, 't': .01}
dfa = {'wind': 0.0, 'snow': .0, 'has_weight': True,
       'has_wind': False, 'has_snow': False}
mesh.attributes.update(ma)
mesh.update_default_vertex_attributes(dva)
mesh.update_default_face_attributes(dfa)


# set constraints
constraints = []

# line constraint
vkey = list(mesh.vertices_where({'x': 10, 'y': 10}))[0]
line = Line(Point(12, 0, -1), Point(10, 10, -1))
xyz = mesh.vertex_attributes(vkey, 'xyz')
constraints.append(Constraint(line, vertex_index[vkey], location=xyz))

# plane constraint
vkey = list(mesh.vertices_where({'x': 0, 'y': 0}))[0]
plane = Plane(Point(2, 2, 0), Vector(1, 0.8, 0.5))
xyz = mesh.vertex_attributes(vkey, 'xyz')
constraints.append(Constraint(plane, vertex_index[vkey], location=xyz))

# curve constraint
vkey = list(mesh.vertices_where({'x': 0, 'y': 10}))[0]
curve = Curve([(-5, 7, 0), (3, 5, 0), (5, 10, 7)], 2)
xyz = mesh.vertex_attributes(vkey, 'xyz')
constraints.append(Constraint(curve, vertex_index[vkey], location=xyz))


# run iterative mesh solver
mesh.fd_iter_numpy(constraints, tolerance=1)


# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

viewer.add(mesh)

for vertex in fixed:
    viewer.add(Point(* mesh.vertex_attributes(vertex, 'xyz')), size=20, color=(0, 0, 0))

for constraint in Constraint.instances:
    if isinstance(constraint, CurveConstraint):
        pts = curve.points_at([d/30 for d in range(0, 30)])
        viewer.add(Polyline(pts), linewidth=5, linecolor=(0, 1, 1))
    else:
        viewer.add(constraint.geometry, linewidth=5, linecolor=(0, 1, 1))

for vertex in fixed:
    a = Point(* mesh.vertex_attributes(vertex, 'xyz'))
    b = a - Vector(* mesh.vertex_attributes(vertex, ['_rx', '_ry', '_rz']))
    viewer.add(Line(a, b), linewidth=3, linecolor=(0, 0, 1))

viewer.run()
