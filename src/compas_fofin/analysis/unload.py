"""Compute the geometry of the prestressed but not-yet-loaded materialised cablenet.

This script *relaxes* the materialised cablenet without loads (before the first concrete is applied).
It updates

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from numpy import array
from numpy import float64

import compas
import compas_hilo

from compas.numerical import dr_numpy

from compas_hilo.datastructures import Shell

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', '..', 'data')

FILE_I = os.path.join(DATA, 'cablenet-materialised.json')
FILE_O = os.path.join(DATA, 'cablenet-unloaded.json')

# load a cablenet
# from a json file containing the unloaded, materialised state.

shell = Shell.from_json(FILE_I)

boundary = set(shell.vertices_on_boundary())

for key, attr in shell.vertices_where({'is_beam': True}, True):
    attr['is_anchor'] = True
    nbrs = shell.vertex_neighbors(key)
    for nbr in nbrs:
        if nbr in boundary:
            pass
        else:
            shell.set_vertex_attribute(nbr, 'is_anchor', False)

keys = [128, 148, 467, 367, 63, 91, 598, 640, 825, 858, 873, 862, 362, 242]
shell.set_vertices_attribute('is_anchor', False, keys=keys)

# extract data for the relaxation process

key_index = shell.key_index()
uv_index  = {(u, v): index for index, (u, v) in enumerate(shell.edges_where({'is_edge': True}))}

fixed  = [key_index[key] for key in shell.vertices_where({'is_anchor': True})]
xyz    = array(shell.get_vertices_attributes('xyz'), dtype=float64)
p      = array(shell.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)

edges  = [(key_index[u], key_index[v]) for u, v in shell.edges_where({'is_edge': True})]
qpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
fpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
lpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
l0     = array([attr['l0'] for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
E      = array([attr['E'] * 1e+6 for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
radius = array([attr['r'] for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))

# relax the cablenet

xyz, q, f, l, r = dr_numpy(xyz, edges, fixed, p, qpre, fpre, lpre, l0, E, radius, kmax=15000)

# update the data structure

for key, attr in shell.vertices(True):
    index = key_index[key]

    attr['x'] = xyz[index, 0]
    attr['y'] = xyz[index, 1]
    attr['z'] = xyz[index, 2]
    attr['rx'] = r[index, 0]
    attr['ry'] = r[index, 1]
    attr['rz'] = r[index, 2]

for u, v, attr in shell.edges_where({'is_edge': True}, True):
    index = uv_index[(u, v)]

    attr['f'] = f[index, 0]
    attr['l'] = l[index, 0]

# serialise

shell.to_json(FILE_O)
