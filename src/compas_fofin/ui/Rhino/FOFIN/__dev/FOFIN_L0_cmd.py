from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas_fofin.analysis import mesh_unstressed_lengths

__commandname__ = "FOFIN_L0"


def RunCommand(is_interactive):
    if 'FOFIN' not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky['FOFIN']

    if not FOFIN['cablenet']:
        print('There is no cablenet.')
        return

    mesh_unstressed_lengths(FOFIN['cablenet'])

    FOFIN['cablenet'].draw(layer=FOFIN['settings']['layer'], clear_layer=True, settings=FOFIN['settings'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
