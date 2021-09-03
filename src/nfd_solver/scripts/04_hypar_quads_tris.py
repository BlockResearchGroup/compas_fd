from os import path
import sys
sys.path.append(path.dirname(path.dirname(__file__)))

from compas.datastructures import Mesh, mesh_subdivide
from compas_view2 import app

from nfd import nfd_ur
from _helpers import mesh_update


# =================================================
# IO
# =================================================
HERE = path.dirname(__file__)
FILE_I = path.join(HERE, '..', 'data', 'in_hypar_mesh.json')
FILE_O = path.join(HERE, '..', 'data', 'out_hypar_mesh_04.json')
mesh = Mesh.from_json(FILE_I)


# =================================================
# input mesh
# =================================================
mesh.vertices_attribute('is_anchor', True,
                        mesh.vertices_where({'vertex_degree': 2}))

mesh = mesh_subdivide(mesh, scheme='quad', k=2)
faces_to_split = (mesh.get_any_face() for _ in range(200))
for face in faces_to_split:
    v = mesh.face_vertices(face)
    mesh.split_face(face, v[0], v[2])

bounds = mesh.edges_on_boundaries()[0]
mesh.edges_attribute('q_pre', 20, bounds)

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
P = mesh.vertices_attributes(['px', 'py', 'pz'])
S = mesh.faces_attribute('s_pre')
Q = mesh.edges_attribute('q_pre')


# =================================================
# run solver
# =================================================
xyz, r, s, f = nfd_ur(mesh, S, Q, vertex_loads=P, kmax=10,
                      s_calc=1, s_tol=.05, xyz_tol=.01)
mesh_update(mesh, xyz, r, s, f)


# =================================================
# visualisation
# =================================================
viewer = app.App()
viewer.add(mesh)
viewer.show()


# =================================================
# output
# =================================================
mesh.to_json(FILE_O)
