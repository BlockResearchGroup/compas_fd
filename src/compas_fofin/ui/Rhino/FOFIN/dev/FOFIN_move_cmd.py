from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import rhinoscriptsyntax as rs

from Rhino.Geometry import Point3d

import compas_rhino
from compas_rhino.ui import CommandMenu
from compas_fofin.rhino import CablenetHelper

find_object = sc.doc.Objects.Find


__commandname__ = "FOFIN_move"


def find_constraint(name):
    rail = None
    if name:
        guids = compas_rhino.get_objects(name=name)
        if len(guids) == 1:
            otype = rs.ObjectType(guids[0])
            if otype == rs.filter.curve:
                rail = find_object(guids[0])
    return rail


def move_vertex(cablenet, settings):
    key = CablenetHelper.select_vertex(cablenet)
    if key is None:
        return

    constraint = None
    name = cablenet.vertex[key]['constraint']
    rail = find_constraint(name)
    if rail:
        constraint = rail.Geometry
        if CablenetHelper.move_vertex(cablenet, key, constraint=constraint, allow_off=False):
            x, y, z = cablenet.vertex_coordinates(key)
            _, t = rail.Geometry.ClosestPoint(Point3d(x, y, z), 0.0)
            cablenet.set_vertex_attribute(key, 'param', t)
            cablenet.draw(layer=settings['layer'], clear_layer=True, settings=settings)
    else:
        if CablenetHelper.move_vertex(cablenet, key):
            cablenet.draw(layer=settings['layer'], clear_layer=True, settings=settings)


def move_vertices(cablenet, settings):
    keys = CablenetHelper.select_vertices(cablenet)
    if not keys:
        return
    if CablenetHelper.move_vertices(cablenet, keys):
        cablenet.draw(layer=settings['layer'], clear_layer=True, settings=settings)


config = {
    "name": "move",
    "message": "Move one or more vertices",
    "options": [
        {
            "name": "vertex",
            "action": move_vertex,
        },
        {
            "name": "vertices",
            "action": move_vertices
        }
    ]
}


def RunCommand(is_interactive):
    if 'FOFIN' not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky['FOFIN']
    if not FOFIN['cablenet']:
        return

    cablenet = FOFIN['cablenet']
    settings = FOFIN['settings']

    menu = CommandMenu(config)
    action = menu.select_action()
    if action:
        action['action'](cablenet, settings)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
