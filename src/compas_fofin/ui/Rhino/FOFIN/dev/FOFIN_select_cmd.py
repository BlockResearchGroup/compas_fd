from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino

from compas_rhino.ui import CommandMenu
from compas_fofin.rhino import CablenetHelper


__commandname__ = "FOFIN_select"


def match_edges(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split(".")[2].split("-")
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_vertices(diagram, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(diagram.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split(".")
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def highlight_edges(diagram, keys):
    guids = match_edges(diagram, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def highlight_vertices(diagram, keys):
    guids = match_vertices(diagram, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


# ==============================================================================
# commands
# ==============================================================================


def select_boundary_vertices(cablenet):
    keys = list(cablenet.vertices_on_boundary())
    highlight_vertices(cablenet, keys)
    return keys


def select_anchored_vertices(cablenet):
    keys = list(cablenet.vertices_where({"is_anchor": True}))
    highlight_vertices(cablenet, keys)
    return keys


def select_all_vertices(cablenet):
    keys = list(cablenet.vertices())
    highlight_vertices(cablenet, keys)
    return keys


def select_continuous_edges(cablenet):
    keys = CablenetHelper.select_edges(cablenet)
    keys = CablenetHelper.select_continuous_edges(cablenet, keys)
    highlight_edges(cablenet, keys)
    return keys


def select_parallel_edges(cablenet):
    keys = CablenetHelper.select_edges(cablenet)
    keys = CablenetHelper.select_parallel_edges(cablenet, keys)
    highlight_edges(cablenet, keys)
    return keys


def select_boundary_edges(cablenet):
    keys = list(cablenet.edges_on_boundary())
    highlight_edges(cablenet, keys)
    return keys


config = {
    "name": "select",
    "message": "Select component",
    "options": [
        {
            "name": "vertices",
            "message": "Select vertices",
            "options": [
                {
                    "name": "boundary",
                    "message": "Select all boundary vertices",
                    "action": select_boundary_vertices
                },
                {
                    "name": "anchored",
                    "message": "Select all anchored vertices",
                    "action": select_anchored_vertices
                },
                {
                    "name": "all",
                    "message": "Select all vertices",
                    "action": select_all_vertices
                }
            ]
        },
        {
            "name": "edges",
            "message": "Select edges",
            "options": [
                {
                    "name": "continuous",
                    "message": "Select continuous edges",
                    "action": select_continuous_edges
                },
                {
                    "name": "parallel",
                    "message": "Select parallel edges",
                    "action": select_parallel_edges
                },
                {
                    "name": "boundary",
                    "message": "Select all boundary edges",
                    "action": select_boundary_edges
                }
            ]
        }
    ]
}


# ==============================================================================
# Command
# ==============================================================================


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    rs.UnselectAllObjects()

    FOFIN = sc.sticky["FOFIN"]

    if not FOFIN["cablenet"]:
        print("There is no cablenet.")
        return

    cablenet = FOFIN["cablenet"]

    menu = CommandMenu(config)
    action = menu.select_action()
    if action:
        action["action"](cablenet)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
