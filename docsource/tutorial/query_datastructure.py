import os
import random

import compas

from compas.files import OBJReader
from compas.utilities import flatten
from compas.utilities import i_to_red
from compas.utilities import i_to_blue

from compas_fofin.datastructures import Cablenet

from compas_plotters import MeshPlotter

# ==============================================================================
# Make a cablenet
# ==============================================================================

# FILE = compas.get('quadmesh.obj')
# cablenet = Cablenet.from_obj(FILE)

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'lines.obj')
FILE_O = os.path.join(HERE, 'lines.json')

obj = OBJReader(FILE_I)
lines = [[obj.vertices[u], obj.vertices[v]] for u, v in obj.lines]

cablenet = Cablenet.from_lines(lines, delete_boundary_face=True)

# ==============================================================================
# Select a starting edge
# ==============================================================================

start = random.choice(list(set(cablenet.edges()) - set(cablenet.edges_on_boundary())))

# ==============================================================================
# Continuous edges and parallel edges
# ==============================================================================

continuous = cablenet.get_continuous_edges(start)
parallel = cablenet.get_parallel_edges(start, aligned=True)
faces = cablenet.get_face_strip(start)

chained = cablenet.get_continuous_edges(start, aligned=True)
chain = list(flatten(chained[::2] + chained[-1:]))

# ==============================================================================
# Visualize
# ==============================================================================

edgecolor = {key: i_to_red(index / len(continuous)) for index, key in enumerate(continuous)}
vertexcolor = {key: i_to_red(index / len(chain)) for index, key in enumerate(chain)}

arrows = [{
    'start': cablenet.vertex_coordinates(start[0]),
    'end': cablenet.vertex_coordinates(start[1]),
    'color': (1.0, 0.0, 0.0)
}]
for u, v in parallel:
    if u not in start and v not in start:
        arrows.append({
            'start': cablenet.vertex_coordinates(u),
            'end': cablenet.vertex_coordinates(v),
            'color': (0.0, 1.0, 0.0)
        })

facecolor = {key: i_to_blue(index / len(faces)) for index, key in enumerate(faces)}

plotter = MeshPlotter(cablenet, figsize=(10, 7))
plotter.draw_edges(width={key: 2.0 for key in continuous})
plotter.draw_vertices(radius=0.04, facecolor=vertexcolor)
plotter.draw_arrows2(arrows)
plotter.draw_faces(facecolor=facecolor, keys=faces, text={key: str(index) for index, key in enumerate(faces)})
plotter.show()

# ==============================================================================
# Export
# ==============================================================================

cablenet.to_json(FILE_O)
