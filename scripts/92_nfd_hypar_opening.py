from os import path

from compas.datastructures import Mesh, mesh_subdivide
from compas_view2 import app

from compas_fd.nfd import nfd_ur_numpy
from _nfd_helpers import mesh_update


# =================================================
# IO
# =================================================

HERE = path.dirname(__file__)
FILE_I = path.join(HERE, '..', 'data', 'in_hypar_mesh.json')
mesh = Mesh.from_json(FILE_I)


# =================================================
# input mesh
# =================================================

mesh.vertices_attribute('is_anchor', True,
                        mesh.vertices_where({'vertex_degree': 2}))

central_vertex = 3
mesh.delete_vertex(3)

mesh = mesh_subdivide(mesh, scheme='quad', k=3)
mesh.quads_to_triangles()

in_bounds, out_bounds = sorted(mesh.edges_on_boundaries(), key=len)
mesh.edges_attribute('q_pre', 11, in_bounds)
mesh.edges_attribute('q_pre', 30, out_bounds)

dva = {'rx': .0, 'ry': .0, 'rz': .0,
       'px': .0, 'py': .0, 'pz': .0,
       'is_anchor': False}
dea = {'q_pre': .0}
dfa = {'s_pre': [1.0, 1.0, 0.0]}

mesh.update_default_vertex_attributes(dva)
mesh.update_default_edge_attributes(dea)
mesh.update_default_face_attributes(dfa)


# =================================================
# get mesh data
# =================================================

fixed = [mesh.key_index()[v] for v in mesh.vertices_where({'is_anchor': True})]
P = mesh.vertices_attributes(['px', 'py', 'pz'])
S = mesh.faces_attribute('s_pre')
Q = mesh.edges_attribute('q_pre')


# =================================================
# solver
# =================================================

xyz, r, f, _, s = nfd_ur_numpy(mesh, fixed, S, force_density_goals=Q, vertex_loads=P,
                               kmax=10, stress_flag=1, stress_tol=.05, xyz_tol=.01)
mesh_update(mesh, xyz, r, s, f)


# =================================================
# viz
# =================================================

viewer = app.App()
viewer.add(mesh)
viewer.show()
