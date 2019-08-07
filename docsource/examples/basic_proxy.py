import os
import json
import compas
import compas_fofin

from compas.remote import Proxy
from compas_fofin.datastructures import Shell
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'hypar.json')

fofin = Proxy('compas_fofin.fofin')

shell = Shell.from_json(FILE)

shell.data = fofin.update_xyz_proxy(shell.data)

plotter = MeshPlotter(shell, figsize=(8, 5))
plotter.draw_vertices()
plotter.draw_edges()
plotter.show()
