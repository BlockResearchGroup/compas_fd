import os
import json
import compas
import compas_fofin

from compas.remote import Proxy
from compas_fofin.datastructures import Shell
from compas_fofin.fofin import fofin_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'hypar.json')

print(FILE)

proxy = Proxy('compas_fofin.fofin')

with open(FILE, 'r') as f:
    data = json.load(f)
    shell = Shell.from_data(data['shell'])

data = proxy.fofin_numpy_proxy(shell.to_data())
shell.data = data

plotter = MeshPlotter(shell, figsize=(8, 5))

plotter.draw_vertices()
plotter.draw_edges()

plotter.show()
