from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import scriptcontext as sc

import compas_rhino
import compas_fofin

from compas_rhino.ui import CommandMenu
from compas_fofin.datastructures import Cablenet


__commandname__ = "FOFIN_from"


HERE = compas_rhino.get_document_dirname()
HERE = HERE or os.path.dirname(compas_fofin.__file__)


def create_cablenet_from_obj(settings):
    folder = settings["file.dir"] or HERE
    filepath = compas_rhino.select_file(folder=folder, filter="obj")
    if not filepath:
        return
    cablenet = Cablenet.from_obj(filepath)
    return cablenet


def create_cablenet_from_json(settings):
    folder = settings["file.dir"] or HERE
    filepath = compas_rhino.select_file(folder=folder, filter="json")
    if not filepath:
        return
    cablenet = Cablenet.from_json(filepath)
    return cablenet


def create_cablenet_from_lines(settings):
    guids = compas_rhino.select_lines()
    if not guids:
        return
    lines = compas_rhino.get_line_coordinates(guids)
    cablenet = Cablenet.from_lines(lines)
    return cablenet


def create_cablenet_from_mesh(settings):
    guid = compas_rhino.select_mesh()
    if not guid:
        return
    cablenet = Cablenet.from_rhinomesh(guid)
    return cablenet


def create_cablenet_from_surface(settings):
    guid = compas_rhino.select_surface()
    if not guid:
        return
    cablenet = Cablenet.from_rhinosurface(guid)
    return cablenet


config = {
    "name": "create",
    "message": "Create cablenet",
    "options": [
        {
            "name": "from_obj",
            "action": create_cablenet_from_obj,
        },
        {
            "name": "from_json",
            "action": create_cablenet_from_json,
        },
        {
            "name": "from_lines",
            "action": create_cablenet_from_lines,
        },
        {
            "name": "from_mesh",
            "action": create_cablenet_from_mesh,
        },
        {
            "name": "from_surface",
            "action": create_cablenet_from_surface,
        }
    ]
}


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]
    settings = FOFIN["settings"]
    cablenet = FOFIN["cablenet"]

    menu = CommandMenu(config)
    action = menu.select_action()
    if action:
        del FOFIN["cablenet"]
        cablenet = action["action"](settings)
        cablenet.draw(layer=settings["layer"], clear_layer=True, settings=settings)
        FOFIN["cablenet"] = cablenet


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
