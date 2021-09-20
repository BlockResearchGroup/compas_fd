import os

from compas.utilities import Colormap

from compas_fd.datastructures import CableMesh
from compas_fd.analysis import mesh_materialize_cables

from compas_plotters import MeshPlotter

# ==============================================================================
# Create a CableMesh
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar_materialized.json')
FILE_P = os.path.join(HERE, 'hypar_materialized.png')

CableMesh = CableMesh.from_json(FILE_I)

# ==============================================================================
# Materialize
# ==============================================================================

mesh_materialize_cables(CableMesh)

# ==============================================================================
# Visualize
# ==============================================================================

edges = list(CableMesh.edges_where({'_is_edge': True}))

stress = [CableMesh.stress(key) for key in edges]
cmap = Colormap(stress, 'rgb')
edgecolor = {key: cmap(s) for key, s in zip(edges, stress)}

utilization = [CableMesh.stress(key) / CableMesh.edge_attribute(key, 'yield') for key in edges]
cmap = Colormap(utilization, 'red')
edgecolor = {key: cmap(u) for key, u in zip(edges, utilization)}

print(min(utilization))
print(max(utilization))

plotter = MeshPlotter(CableMesh, figsize=(16, 9))
plotter.draw_vertices(radius=0.05, facecolor={key: (0.0, 0.0, 0.0) for key in CableMesh.vertices_where({'is_anchor': True})})
plotter.draw_edges(width=2.0, color=edgecolor, keys=edges)

plotter.save(FILE_P, dpi=150)
# plotter.show()

# ==============================================================================
# Export
# ==============================================================================

CableMesh.to_json(FILE_O)
