from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

from Rhino.Geometry import Point3d

import compas_rhino

find_object = sc.doc.Objects.Find


__commandname__ = "FOFIN_constrain"


def find_constraint(name):
    rail = None
    if name:
        guids = compas_rhino.get_objects(name=name)
        if len(guids) == 1:
            otype = rs.ObjectType(guids[0])
            if otype == rs.filter.curve:
                rail = find_object(guids[0])
    return rail


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky["FOFIN"]
    if not FOFIN["cablenet"]:
        return

    for key, attr in FOFIN["cablenet"].vertices(True):
        rail = find_constraint(attr["constraint"])
        if rail:
            if attr["param"] is None:
                _, t = rail.Geometry.ClosestPoint(Point3d(attr["x"], attr["y"], attr["z"]), 0.0)
                attr["param"] = t
            else:
                t = attr["param"]
            point = rs.EvaluateCurve(rail, t)
            x, y, z = list(point)
            attr["x"] = x
            attr["y"] = y
            attr["z"] = z

    FOFIN["cablenet"].draw(layer=FOFIN["settings"]["layer"], clear_layer=True, settings=FOFIN["settings"])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
