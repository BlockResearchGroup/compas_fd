from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino

from compas_rhino.ui import CommandMenu
from compas_fofin.rhino import CablenetHelper


__commandname__ = "FOFIN_attributes"


def update_cablenet_attributes(cablenet, settings):
    return compas_rhino.update_settings(cablenet.attributes)


def update_vertex_attributes(cablenet, settings):
    keys = CablenetHelper.select_vertices(cablenet)
    if keys:
        return CablenetHelper.update_vertex_attributes(cablenet, keys)


def update_edge_attributes(cablenet, settings):
    keys = CablenetHelper.select_edges(cablenet)
    if keys:
        return CablenetHelper.update_edge_attributes(cablenet, keys)


def update_face_attributes(cablenet, settings):
    keys = CablenetHelper.select_faces(cablenet)
    if keys:
        return CablenetHelper.update_face_attributes(cablenet, keys)


config = {
    "name": "attributes",
    "message": "Update attributes",
    "options": [
        {
            "name": "cablenet",
            "message": "Cablenet attributes",
            "action": update_cablenet_attributes,
        },
        {
            "name": "vertices",
            "message": "Vertex attributes",
            "action": update_vertex_attributes,
        },
        {
            "name": "edges",
            "message": "Edge attributes",
            "action": update_edge_attributes,
        },
        {
            "name": "faces",
            "message": "Face attributes",
            "action": update_face_attributes,
        },
    ]
}


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]

    if not FOFIN["cablenet"]:
        return

    cablenet = FOFIN["cablenet"]
    settings = FOFIN["settings"]

    menu = CommandMenu(config)
    action = menu.select_action()
    if action:
        if action["action"](cablenet, settings):
            cablenet.draw(layer=settings["layer"], clear_layer=True, settings=settings)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
