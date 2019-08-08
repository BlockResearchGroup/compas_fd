import os
from compas_fofin.datastructures import Shell
from compas_fofin.analysis import mesh_materialize_cables
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar.json')

shell = Shell.from_json(FILE_I)

mesh_materialize_cables(shell)

sizes = shell.get_edges_attribute('size')
r = shell.get_edges_attribute('r')
l = shell.get_edges_attribute('l')
l0 = shell.get_edges_attribute('l0')

print(sizes)
print(r)
print(["{:.4f}".format(l / l0) for l, l0 in zip(l, l0)])

plotter = MeshPlotter(shell, figsize=(10, 7))
plotter.draw_vertices(radius=0.05)
plotter.draw_edges()
plotter.show()

shell.to_json(FILE_O)
