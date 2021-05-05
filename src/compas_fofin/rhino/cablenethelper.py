from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.modifiers import EdgeModifier
from compas_rhino.modifiers import VertexModifier
from compas_rhino.selectors import FaceSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import VertexSelector
from ast import literal_eval

import compas
import compas_rhino

from compas.utilities import flatten

if compas.IPY:
    import rhinoscriptsyntax as rs


__all__ = ['CablenetHelper']


def match_vertices(cablenet, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(cablenet.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def match_edges(cablenet, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(cablenet.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_faces(cablenet, keys):
    temp = compas_rhino.get_objects(name="{}.face.*".format(cablenet.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def select_vertices(cablenet, keys):
    guids = match_vertices(cablenet, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def select_edges(cablenet, keys):
    guids = match_edges(cablenet, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def select_faces(cablenet, keys):
    guids = match_faces(cablenet, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


class CablenetHelper(VertexSelector,
                     EdgeSelector,
                     FaceSelector,
                     VertexModifier,
                     EdgeModifier):
    """A cablenet helper groups functionality for selecting and modifying cablenet
    vertices and edges in Rhino.
    """

    @staticmethod
    def highlight_faces(cablenet, keys):
        select_faces(cablenet, keys)

    @staticmethod
    def select_parallel_edges(cablenet, keys):
        keys = [cablenet.get_parallel_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        select_edges(cablenet, keys)
        return keys

    @staticmethod
    def select_continuous_edges(cablenet, keys):
        keys = [cablenet.get_continuous_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        select_edges(cablenet, keys)
        return keys

    @staticmethod
    def select_boundary_faces(cablenet):
        keys = cablenet.faces_on_boundary()
        select_faces(cablenet, keys)
        return keys

    @staticmethod
    def select_face_strip(cablenet, fkey):
        strip = cablenet.face_strip(fkey)
        select_faces(cablenet, strip)
        return strip

    @staticmethod
    def update_vertex_attributes(cablenet, keys, names=None):
        if not names:
            names = cablenet.default_vertex_attributes.keys()
        names = sorted(names)
        values = [cablenet.vertex[keys[0]][name] for name in names]
        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != cablenet.vertex[key][name]:
                        values[i] = '-'
                        break

        values = map(str, values)
        values = compas_rhino.update_named_values(names, values)

        if values:
            for name, value in zip(names, values):
                if value != '-':
                    for key in keys:
                        try:
                            value = literal_eval(value)
                        except (SyntaxError, ValueError, TypeError):
                            pass
                        cablenet.vertex_attribute(key, name, value)

            return True
        return False

    @staticmethod
    def update_edge_attributes(cablenet, keys, names=None):
        if not names:
            names = cablenet.default_edge_attributes.keys()
        names = sorted(names)

        key = keys[0]
        values = cablenet.edge_attributes(key, names)

        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != cablenet.edge_attribute(key, name):
                        values[i] = '-'
                        break

        values = map(str, values)
        values = compas_rhino.update_named_values(names, values)

        if values:
            for name, value in zip(names, values):
                if value != '-':
                    for key in keys:
                        try:
                            value = literal_eval(value)
                        except (SyntaxError, ValueError, TypeError):
                            pass
                        cablenet.edge_attribute(key, name, value)

            return True
        return False

    @staticmethod
    def update_face_attributes(cablenet, keys, names=None):
        if not names:
            names = cablenet.default_face_attributes.keys()
        names = sorted(names)

        key = keys[0]
        values = cablenet.face_attributes(key, names)

        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != cablenet.face_attribute(key, name):
                        values[i] = '-'
                        break

        values = map(str, values)
        values = compas_rhino.update_named_values(names, values)

        if values:
            for name, value in zip(names, values):
                if value != '-':
                    for key in keys:
                        try:
                            value = literal_eval(value)
                        except (SyntaxError, ValueError, TypeError):
                            pass
                        cablenet.face_attribute(key, name, value)

            return True
        return False


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
