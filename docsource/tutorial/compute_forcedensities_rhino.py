import os
from compas.utilities import i_to_black
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist
from compas.remote import Proxy

fofin = Proxy('compas_fofin.fofin')

HERE = os.path.dirname(__file__)
FILE_I = os.path.join(HERE, 'hypar.json')
FILE_O = os.path.join(HERE, 'hypar.json')

shell = Shell.from_json(FILE_I)
shell.set_vertices_attribute('t', 0.005)
shell.attributes['density'] = 22

q = shell.get_edges_attribute('q')
qmin = min(q)
qmax = max(q)
print(qmin, qmax)

shell.data = fofin.find_q_proxy(shell.to_data(), qmin=0.1, qmax=20)
shell.data = fofin.update_xyz_proxy(shell.to_data())

q = shell.get_edges_attribute('q')
qmin = min(q)
qmax = max(q)
print(qmin, qmax)

z = shell.get_vertices_attribute('z')
zmin = min(z)
zmax = max(z)
vertexcolor = {key: i_to_black((attr['z'] - zmin) / (zmax - zmin)) for key, attr in shell.vertices(True)}

artist = ShellArtist(shell, layer="Shell")
artist.clear_layer()
artist.draw_vertices()
artist.draw_forces()
artist.draw_mesh()
