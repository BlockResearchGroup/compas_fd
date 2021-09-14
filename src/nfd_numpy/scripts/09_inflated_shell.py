from os import path
import sys
sys.path.append(path.dirname(path.dirname(__file__)))

from compas.datastructures import Mesh, mesh_subdivide
from compas_view2 import app

from nfd import nfd_ur_numpy
from _helpers import mesh_update


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
mesh.vertices_attribute('z', 0, mesh.vertices_where({'vertex_degree': 2}))

mesh = mesh_subdivide(mesh, scheme='quad', k=1)
# mesh.quads_to_triangles()

bounds = mesh.edges_on_boundaries()[0]
mesh.edges_attribute('q_pre', -10, bounds)

dva = {'rx': .0, 'ry': .0, 'rz': .0,
       'is_anchor': False}
dea = {'q_pre': .0}
dfa = {'s_pre': [-1.0, -1.0, 0.0],
       'px': .0, 'py': .0, 'pz': -.05}

mesh.update_default_vertex_attributes(dva)
mesh.update_default_edge_attributes(dea)
mesh.update_default_face_attributes(dfa)


# =================================================
# get mesh data
# =================================================
P1 = mesh.faces_attributes(['px', 'py', 'pz'])
P2 = [-0.2 * p for load_vec in P1 for p in load_vec]
S = mesh.faces_attribute('s_pre')
Q = mesh.edges_attribute('q_pre')


# =================================================
# run solver
# =================================================
xyz, r, s, f = nfd_ur_numpy(mesh, S, Q, local_face_loads=P1,
                            global_face_loads=P2, kmax=5, s_calc=1)
mesh_update(mesh, xyz, r, s, f)


# =================================================
# visualisation
# =================================================
viewer = app.App()
viewer.add(mesh)
viewer.show()
