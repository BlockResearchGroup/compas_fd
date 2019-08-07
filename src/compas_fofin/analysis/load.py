"""Load the materialised *cablenet* with the first layer of concrete.

From the forces in the cablenet under influence of the weigth of the first layer of concret,
the stress state in each of the cable elements (or rods) can be computed.

This script applies the loads and *relaxes* the cablenet.
Finally, it updates

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
from compas_hilo.utilities import NumericalSelfweightCalculator

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', '..', 'data')

FILE_I = os.path.join(DATA, 'cablenet-unloaded.json')
FILE_O = os.path.join(DATA, 'cablenet-loaded-c1.json')

# load a cablenet
# from a json file containing the unloaded, materialised state.

shell = Shell.from_json(FILE_I)

# extract data fro the relaxation process

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

# compute the weight of the frist layer of concrete
# note: this should be based on the designed geometry
#       not the geometry of the unloaded state

density = shell.attributes['density']
density = 0.5 * (12.8 + 18.6)
density = 0.5 * (12.8 + 14.0)

shell.set_vertices_attribute('c1', 0.03)

calculate_sw = NumericalSelfweightCalculator(shell, density=density, thickness_attr_name='c1')
sw = calculate_sw(xyz)
p[:, 2] = - 1.0 * sw[:, 0]

# relax the cablenet

xyz, q, f, l, r = dr_numpy(xyz, edges, fixed, p, qpre, fpre, lpre, l0, E, radius, kmax=15000, tol1=0.01)

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
