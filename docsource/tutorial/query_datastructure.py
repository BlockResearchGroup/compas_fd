import os
import random
import compas
from compas.utilities import flatten
from compas_fofin.datastructures import Cablenet
from compas_plotters import MeshPlotter

# HERE = os.path.dirname(__file__)
# FILE_I = os.path.join(HERE, 'quadmesh.obj')

FILE = compas.get('quadmesh.obj')

cablenet = Cablenet.from_obj(FILE)

start = random.choice(list(set(cablenet.edges()) - set(cablenet.edges_on_boundary())))

notaligned = cablenet.get_continuous_edges(start)
aligned = cablenet.get_continuous_edges(start, aligned=True)

parallel = cablenet.get_parallel_edges(start)

color = {uv: '#00ff00' for uv in parallel}
color.update({uv: '#ff0000' for uv in notaligned})

alignedflat = flatten(aligned[::2] + aligned[-1:])

plotter = MeshPlotter(cablenet, figsize=(10, 7))
plotter.draw_edges(width={key: 2.0 for key in notaligned}, color=color)
plotter.draw_vertices(text={key: index for index, key in enumerate(alignedflat)}, radius=0.05)
plotter.show()

