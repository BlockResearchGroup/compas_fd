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

mesh = mesh_subdivide(mesh, scheme='quad', k=3)
mesh.quads_to_triangles()

# get ring of vertices around central vertex
central_vertex = 3
ring_size = 3
ring_all = mesh.vertex_neighborhood(central_vertex, ring=ring_size)
ring_in = mesh.vertex_neighborhood(central_vertex, ring=ring_size - 1)
ring = set(ring_all) - set(ring_in)
mesh.vertices_attributes(['z', 'is_anchor'], [25, True], ring)

# triangulate top faces at supports
fva = mesh.face_vertex_after
for v in ring:
    faces = mesh.vertex_faces(v)

    for face in faces:
        vts = mesh.face_vertices(face)
        v_count = len(vts)
        if v_count != 4:
            continue
        w = fva(face, fva(face, v))
        if not mesh.vertex_attribute(w, 'is_anchor'):
            continue
        mesh.split_face(face, v, w)

# delete vertices inside support ring
for v in ring_in:
    mesh.delete_vertex(v)

bounds = mesh.edges_on_boundaries()[0]
mesh.edges_attribute('q_pre', 30, bounds)

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
xyz, r, s, f = nfd_ur_numpy(mesh, S, Q, vertex_loads=P, kmax=10,
                            s_calc=1, s_tol=.001, xyz_tol=.001)
mesh_update(mesh, xyz, r, s, f)


# =================================================
# visualisation
# =================================================
viewer = app.App()
viewer.add(mesh)
viewer.show()
