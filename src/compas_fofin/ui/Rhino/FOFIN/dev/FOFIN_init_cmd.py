from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino

from compas.rpc import Proxy


__commandname__ = "FOFIN_init"


def RunCommand(is_interactive):
    p = Proxy()

    sc.sticky["FOFIN"] = {
        "proxy": p,
        "cablenet": None,
        "settings": {
            "layer": "FOFIN",

            "safety.forces": 1.0,
            "safety.loads": 1.0,
            "safety.selfweight": 1.0,
            "safety.material": 1.0,

            "show.forces": False,
            "show.reactions": False,
            "show.residuals": False,
            "show.loads": False,
            "show.selfweight": False,
            "show.stress": False,
            "show.normals": False,

            "scale.forces": 0.1,
            "scale.reactions": 0.5,
            "scale.residuals": 1.0,
            "scale.loads": 1.0,
            "scale.selfweight": 1.0,
            "scale.stress": 0.1,
            "scale.normals": 0.1,

            "tol.residuals": 0.01,

            "file.dir": compas_rhino.get_document_dirname(),
            "file.name": None
        }
    }


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
