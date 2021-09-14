import os

from compas.utilities import Colormap

from compas_fd.datastructures import CableMesh
from compas_fd.fd import update_xyz_numpy

from compas_plotters import MeshPlotter

# ==============================================================================
# Create a CableMesh
# ==============================================================================

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'lines.json')
FILE_O = os.path.join(HERE, 'hypar.json')
FILE_P = os.path.join(HERE, 'hypar.png')

CableMesh = CableMesh.from_json(FILE_I)

CableMesh.attributes['density'] = 0.0

# ==============================================================================
# Identify anchors
# ==============================================================================

CableMesh.vertices_attribute('is_anchor', True, keys=list(CableMesh.vertices_on_boundary()))

# ==============================================================================
# Compute equilibrium
# ==============================================================================

update_xyz_numpy(CableMesh)

# ==============================================================================
# Visualize
# ==============================================================================

heights = CableMesh.vertices_attribute('z')
cmap = Colormap(heights, 'black')
vertexcolor = {key: cmap(z) for key, z in zip(CableMesh.vertices(), heights)}

forces = CableMesh.edges_attribute('f')
cmap = Colormap(forces, 'rgb')
edgecolor = {key: cmap(f) for key, f in zip(CableMesh.edges(), forces)}

plotter = MeshPlotter(CableMesh, figsize=(16, 9))
plotter.draw_vertices(facecolor=vertexcolor, radius=0.05)
plotter.draw_edges(width=2.0, color=edgecolor)

plotter.save(FILE_P, dpi=150)
# plotter.show()

# ==============================================================================
# Export
# ==============================================================================

CableMesh.to_json(FILE_O)
