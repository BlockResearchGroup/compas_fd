from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino
import compas_fofin

from compas_fofin.datastructures import Cablenet


__commandname__ = "FOFIN_open"


HERE = compas_rhino.get_document_dirname()
HERE = HERE or os.path.dirname(compas_fofin.__file__)


def open_file(settings):
    if not settings["file.dir"]:
        filepath = compas_rhino.select_file(folder=HERE, filter="fofin")
    else:
        filepath = compas_rhino.select_file(folder=settings["file.dir"], filter="fofin")

    if not filepath:
        return

    file_dir = os.path.dirname(filepath)
    file_name = os.path.basename(filepath)

    settings["file.dir"] = file_dir
    settings["file.name"] = file_name

    if not file_name.endswith(".fofin"):
        print("The filename is invalid: {}".format(file_name))
        return

    filepath = os.path.join(file_dir, file_name)

    with open(filepath, "r") as f:
        data = json.load(f)

        if "settings" in data and data["settings"]:
            settings.update(data["settings"])

        if "cablenet" in data and data["cablenet"]:
            cablenet = Cablenet.from_data(data["cablenet"])
            cablenet.draw(layer=settings["layer"], clear_layer=True, settings=settings)
        else:
            cablenet = None

    return cablenet


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]
    settings = FOFIN["settings"]

    cablenet = open_file(settings)
    del FOFIN["cablenet"]
    FOFIN["cablenet"] = cablenet


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
