from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino


__commandname__ = "FOFIN_settings"


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]

    if compas_rhino.update_settings(FOFIN["settings"]):
        if FOFIN["cablenet"]:
            FOFIN["cablenet"].draw(layer=FOFIN["settings"]["layer"], clear_layer=True, settings=FOFIN["settings"])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
