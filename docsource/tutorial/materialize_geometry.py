import os

from compas.utilities import Colormap

from compas_fofin.datastructures import Cablenet
from compas_fofin.analysis import mesh_materialize_cables

from compas_plotters import MeshPlotter

# ==============================================================================
# Create a cablenet
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar_materialized.json')

cablenet = Cablenet.from_json(FILE_I)

# ==============================================================================
# Materialize
# ==============================================================================

mesh_materialize_cables(cablenet)

# ==============================================================================
# Visualize
# ==============================================================================

stress = [cablenet.stress(key) for key in cablenet.edges()]
cmap = Colormap(stress, 'rgb')
edgecolor = {key: cmap(s) for key, s in zip(cablenet.edges(), stress)}

utilization = [cablenet.stress(key) / cablenet.get_edge_attribute(key, 'yield') for key in cablenet.edges()]
cmap = Colormap(utilization, 'red')
edgecolor = {key: cmap(u) for key, u in zip(cablenet.edges(), utilization)}

print(min(utilization))
print(max(utilization))

plotter = MeshPlotter(cablenet, figsize=(10, 7))
plotter.draw_vertices(radius=0.05, facecolor={key: (0.0, 0.0, 0.0) for key in cablenet.vertices_where({'is_anchor': True})})
plotter.draw_edges(width=2.0, color=edgecolor)
plotter.show()

# ==============================================================================
# Export
# ==============================================================================

cablenet.to_json(FILE_O)
