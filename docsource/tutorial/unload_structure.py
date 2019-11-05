import os

from compas.utilities import Colormap

from compas_fofin.datastructures import Cablenet
from compas_fofin.analysis import unload_numpy

from compas_plotters import MeshPlotter

# ==============================================================================
# Create cablenet
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar_materialized.json')
FILE_O = os.path.join(HERE, 'hypar_unloaded.json')

cablenet = Cablenet.from_json(FILE_I)

# ==============================================================================
# Unload the cablenet
# ==============================================================================

unload_numpy(cablenet)

# ==============================================================================
# Visualize
# ==============================================================================

edges = list(cablenet.edges_where({'is_edge': True}))

stress = [cablenet.stress(key) for key in edges]
cmap = Colormap(stress, 'rgb')
edgecolor = {key: cmap(s) for key, s in zip(edges, stress)}

print(stress)

utilization = [cablenet.stress(key) / cablenet.get_edge_attribute(key, 'yield') for key in edges]
# cmap = Colormap(utilization, 'red')
# edgecolor = {key: cmap(u) for key, u in zip(edges, utilization)}

print(min(utilization))
print(max(utilization))

plotter = MeshPlotter(cablenet, figsize=(10, 7))
plotter.draw_vertices(radius=0.05, facecolor={key: (0.0, 0.0, 0.0) for key in cablenet.vertices_where({'is_anchor': True})})
plotter.draw_edges(width=2.0, color=edgecolor, keys=edges)
plotter.show()

# ==============================================================================
# Export
# ==============================================================================

cablenet.to_json(FILE_O)
