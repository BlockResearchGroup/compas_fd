import os

from compas.datastructures import Mesh

import compas_rhino
from compas_rhino.artists import MeshArtist

from _helpers import draw_stresses


HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, '..', 'data', 'out_hypar_mesh_99.json')

layer = 'FoFi'
compas_rhino.clear_layer(layer)
mesh = Mesh.from_json(FILE_I)

# visualisation
# colored = (3, 78, 33)
artist = MeshArtist(mesh, layer + '::Mesh_Out')
artist.draw_mesh()
anchors = list(mesh.vertices_where({'is_anchor': True}))
artist.draw_vertices(anchors, color=(0, 0, 0))
# artist.draw_vertexlabels(color={c: (255, i * 100, 0)
#                          for i, c in enumerate(colored)})
artist.draw_vertexlabels()
# artist.draw_facenormals()
# artist.draw_facelabels()
draw_stresses(mesh, layer, 2)
artist.redraw()
