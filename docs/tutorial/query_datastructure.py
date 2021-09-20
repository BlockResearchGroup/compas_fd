import os
import random

import compas

from compas.files import OBJ
from compas.utilities import flatten
from compas.utilities import i_to_red
from compas.utilities import i_to_blue

from compas_fd.datastructures import CableMesh

from compas_plotters import MeshPlotter

# ==============================================================================
# Make a CableMesh
# ==============================================================================

# FILE = compas.get('quadmesh.obj')
# CableMesh = CableMesh.from_obj(FILE)

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'lines.obj')
FILE_O = os.path.join(HERE, 'lines.json')

obj = OBJ(FILE_I)
lines = [[obj.vertices[u], obj.vertices[v]] for u, v in obj.lines]

CableMesh = CableMesh.from_lines(lines, delete_boundary_face=True)

CableMesh.edges_attribute('_is_edge', False, keys=list(CableMesh.edges_on_boundary()))

# ==============================================================================
# Select a starting edge
# ==============================================================================

start = random.choice(list(set(CableMesh.edges()) - set(CableMesh.edges_on_boundary())))

# ==============================================================================
# Continuous edges and parallel edges
# ==============================================================================

continuous = CableMesh.get_continuous_edges(start)
parallel = CableMesh.get_parallel_edges(start, aligned=True)
faces = CableMesh.get_face_strip(start)

cables = []
for edge in parallel:
    edges = CableMesh.get_continuous_edges(edge)
    cables.append(edges)

chained = CableMesh.get_continuous_edges(start, aligned=True)
chain = list(flatten(chained[::2] + chained[-1:]))

# ==============================================================================
# Visualize
# ==============================================================================

vertexcolor = {key: i_to_red(index / len(chain)) for index, key in enumerate(chain)}

arrows = [{
    'start': CableMesh.vertex_coordinates(start[0]),
    'end': CableMesh.vertex_coordinates(start[1]),
    'color': (1.0, 0.0, 0.0)
}]
for u, v in parallel:
    if u not in start and v not in start:
        arrows.append({
            'start': CableMesh.vertex_coordinates(u),
            'end': CableMesh.vertex_coordinates(v),
            'color': (0.0, 0.0, 0.0)
        })

facecolor = {key: i_to_blue(index / len(faces)) for index, key in enumerate(faces)}

plotter = MeshPlotter(CableMesh, figsize=(10, 7))
plotter.defaults['vertex.radius'] = 0.04
plotter.defaults['edge.width'] = 0.5
plotter.draw_edges(width={key: 3.0 for edges in cables for key in edges})
plotter.draw_vertices(radius={key: 0.06 for key in chain}, facecolor=vertexcolor)
plotter.draw_arrows2(arrows)
plotter.draw_faces(facecolor=facecolor, keys=faces, text={key: str(index) for index, key in enumerate(faces)})
plotter.show()

# ==============================================================================
# Export
# ==============================================================================

CableMesh.to_json(FILE_O)
