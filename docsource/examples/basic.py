import os
import json
import compas
import compas_fofin

from compas_fofin.datastructures import Shell
from compas_fofin.fofin import update_xyz_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'hypar.json')

shell = Shell.from_json(FILE)

update_xyz_numpy(shell)

plotter = MeshPlotter(shell, figsize=(8, 5))
plotter.draw_vertices(facecolor={key: '#ff0000' for key in shell.vertices_where({'is_anchor': True})})
plotter.draw_edges()
plotter.show()
