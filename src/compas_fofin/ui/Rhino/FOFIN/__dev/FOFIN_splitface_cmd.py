from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas.datastructures import mesh_split_face
from compas_fofin.rhino import CablenetHelper


__commandname__ = 'FOFIN_splitface'


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky['FOFIN']
    if not FOFIN['cablenet']:
        return

    fkey = CablenetHelper.select_face(FOFIN['cablenet'])
    if fkey is None:
        return

    u, v = CablenetHelper.select_vertices(FOFIN['cablenet'])

    mesh_split_face(FOFIN['cablenet'], fkey, u, v)

    FOFIN['cablenet'].cull_vertices()

    FOFIN['cablenet'].draw(layer=FOFIN['settings']['layer'], clear_layer=True, settings=FOFIN['settings'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
