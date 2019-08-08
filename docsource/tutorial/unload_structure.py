import os
from compas_fofin.datastructures import Shell
from compas_fofin.analysis import unload_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar.json')

shell = Shell.from_json(FILE_I)

unload_numpy(shell)

plotter = MeshPlotter(shell, figsize=(10, 7))
plotter.draw_vertices(radius=0.05)
plotter.draw_edges()
plotter.show()

shell.to_json(FILE_O)
