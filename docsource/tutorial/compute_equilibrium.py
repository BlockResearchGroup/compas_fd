import os
from compas.utilities import i_to_black
from compas_fofin.datastructures import Shell
from compas_fofin.fofin import update_xyz_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.obj')
FILE_O = os.path.join(HERE, 'hypar.json')

shell = Shell.from_obj(FILE_I)
shell.set_vertices_attribute('is_anchor', True, keys=list(shell.vertices_on_boundary()))

update_xyz_numpy(shell)

z = shell.get_vertices_attribute('z')
zmin = min(z)
zmax = max(z)
vertexcolor = {key: i_to_black((attr['z'] - zmin) / (zmax - zmin)) for key, attr in shell.vertices(True)}

plotter = MeshPlotter(shell, figsize=(10, 7))
plotter.draw_vertices(
    facecolor=vertexcolor,
    radius=0.05)
plotter.draw_edges()
plotter.show()

shell.to_json(FILE_O)
