from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc


__commandname__ = "FOFIN_update_xyz"


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]

    if not FOFIN["cablenet"]:
        print("There is no cablenet.")
        return

    fofin = FOFIN["proxy"]
    fofin.package = "compas_fofin.fofin"

    data = fofin.update_xyz_proxy(FOFIN["cablenet"].to_data())

    FOFIN["cablenet"].data = data
    FOFIN["cablenet"].draw(layer=FOFIN["settings"]["layer"], clear_layer=True, settings=FOFIN["settings"])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
