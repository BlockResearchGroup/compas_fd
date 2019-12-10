from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino


__commandname__ = "FOFIN_to"


HERE = compas_rhino.get_document_dirname()


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]

    if not FOFIN["cablenet"]:
        print("No cablenet to serialise.")
        return

    file_dir = FOFIN["settings"]["file.dir"]
    FOLDER = file_dir or HERE
    file_dir = compas_rhino.select_folder(default=FOLDER)
    if not file_dir:
        print("No directory selected.")
        return
    if not os.path.isdir(file_dir):
        print("The selected directory is invalid: {}".format(file_dir))
        return

    file_name = rs.GetString("File name")

    if not file_name:
        print("No filename provided.")
        return
    if not file_name.endswith(".json"):
        print("The filename is invalid: {}".format(file_name))
        return

    filepath = os.path.join(file_dir, file_name)

    FOFIN["cablenet"].to_json(filepath)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
