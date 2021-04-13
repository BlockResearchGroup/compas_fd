from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

from compas_fofin.rhino import CablenetHelper


__commandname__ = "FOFIN_scaleQ"


def RunCommand(is_interactive):
    if 'FOFIN' not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky['FOFIN']

    if not FOFIN['cablenet']:
        return

    keys = CablenetHelper.select_edges(FOFIN['cablenet'])

    scale = rs.GetReal("Scaling factor", 1.0, 0.1, 10.0)

    if not scale:
        return

    for edge in keys:
        q = FOFIN['cablenet'].get_edge_attribute(edge, 'q')
        FOFIN['cablenet'].set_edge_attribute(edge, 'q', scale * q)

    FOFIN['cablenet'].draw(layer=FOFIN['settings']['layer'], clear_layer=True, settings=FOFIN['settings'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
