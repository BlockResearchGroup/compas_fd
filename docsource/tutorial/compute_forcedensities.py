import os
from compas.utilities import i_to_black
from compas_fofin.datastructures import Shell
from compas_fofin.fofin import find_q_numpy
from compas_fofin.fofin import update_xyz_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar.json')

shell = Shell.from_json(FILE_I)
shell.set_vertices_attribute('t', 0.005)
shell.attributes['density'] = 22

q = shell.get_edges_attribute('q')
qmin = min(q)
qmax = max(q)
print(qmin, qmax)

find_q_numpy(shell, qmin=0.1, qmax=20)
update_xyz_numpy(shell)

q = shell.get_edges_attribute('q')
qmin = min(q)
qmax = max(q)
print(qmin, qmax)

z = shell.get_vertices_attribute('z')
zmin = min(z)
zmax = max(z)
vertexcolor = {key: i_to_black((attr['z'] - zmin) / (zmax - zmin)) for key, attr in shell.vertices(True)}

plotter = MeshPlotter(shell, figsize=(10, 7))
plotter.draw_vertices(
    facecolor=vertexcolor,
    radius=0.05)
plotter.draw_edges()
plotter.show()

shell.to_json(FILE_O)
