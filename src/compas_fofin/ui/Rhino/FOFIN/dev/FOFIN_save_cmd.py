from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_fofin


__commandname__ = "FOFIN_save"


HERE = compas_rhino.get_document_dirname()
HERE = HERE or os.path.dirname(compas_fofin.__file__)


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]

    options = ["save", "save_as"]
    option = rs.GetString("Save the FOFIN session.", options[0], options)

    if not option:
        return

    data = {"settings": FOFIN["settings"], "cablenet": None}

    if FOFIN["cablenet"]:
        data["cablenet"] = FOFIN["cablenet"].to_data()

    file_dir = FOFIN["settings"]["file.dir"]
    file_name = FOFIN["settings"]["file.name"]

    if option == "save":
        if not file_dir:
            file_dir = compas_rhino.select_folder(default=HERE)
            if not file_dir:
                print("No directory selected.")
                return
        if not file_name:
            file_name = rs.GetString("File name")

    elif option == "save_as":
        FOLDER = file_dir or HERE
        file_dir = compas_rhino.select_folder(default=FOLDER)
        if not file_dir:
            print("No directory selected.")
            return
        file_name = rs.GetString("File name")

    FOFIN["settings"]["file.dir"] = file_dir
    FOFIN["settings"]["file.name"] = file_name

    if not os.path.isdir(file_dir):
        print("The selected directory is invalid: {}".format(file_dir))
        return

    if not file_name:
        print("No filename provided.")
        return

    if not file_name.endswith(".fofin"):
        print("The filename is invalid: {}".format(file_name))
        return

    filepath = os.path.join(file_dir, file_name)

    with open(filepath, "w") as f:
        json.dump(data, f)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
