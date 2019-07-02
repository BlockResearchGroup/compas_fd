from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from ast import literal_eval

import compas
import compas_rhino

from compas.utilities import flatten

if compas.IPY:
    import rhinoscriptsyntax as rs

from compas_rhino.selectors import VertexSelector
from compas_rhino.selectors import EdgeSelector
from compas_rhino.selectors import FaceSelector
from compas_rhino.modifiers import VertexModifier
from compas_rhino.modifiers import EdgeModifier
from compas_rhino.modifiers import FaceModifier


__all__ = ['ShellHelper']


def match_vertices(shell, keys):
    temp = compas_rhino.get_objects(name="{}.vertex.*".format(shell.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def match_edges(shell, keys):
    temp = compas_rhino.get_objects(name="{}.edge.*".format(shell.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')[2].split('-')
        u = literal_eval(parts[0])
        v = literal_eval(parts[1])
        if (u, v) in keys or (v, u) in keys:
            guids.append(guid)
    return guids


def match_faces(shell, keys):
    temp = compas_rhino.get_objects(name="{}.face.*".format(shell.name))
    names = compas_rhino.get_object_names(temp)
    guids = []
    for guid, name in zip(temp, names):
        parts = name.split('.')
        key = literal_eval(parts[2])
        if key in keys:
            guids.append(guid)
    return guids


def select_vertices(shell, keys):
    guids = match_vertices(shell, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def select_edges(shell, keys):
    guids = match_edges(shell, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


def select_faces(shell, keys):
    guids = match_faces(shell, keys)
    rs.EnableRedraw(False)
    rs.SelectObjects(guids)
    rs.EnableRedraw(True)


class ShellHelper(VertexSelector,
                  EdgeSelector,
                  FaceSelector,
                  VertexModifier,
                  EdgeModifier):
    """A shell helper groups functionality for selecting and modifying shell
    vertices and edges in Rhino.
    """

    @staticmethod
    def highlight_faces(shell, keys):
        select_faces(shell, keys)

    @staticmethod
    def select_parallel_edges(shell, keys):
        keys = [shell.get_parallel_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        select_edges(shell, keys)
        return keys

    @staticmethod
    def select_continuous_edges(shell, keys):
        keys = [shell.get_continuous_edges(key) for key in keys]
        keys = list(set(list(flatten(keys))))
        select_edges(shell, keys)
        return keys

    @staticmethod
    def select_boundary_faces(shell):
        keys = shell.faces_on_boundary()
        select_faces(shell, keys)
        return keys

    @staticmethod
    def select_face_strip(shell, fkey):
        strip = shell.get_face_strip(fkey)
        select_faces(shell, strip)
        return strip

    @staticmethod
    def update_vertex_attributes(shell, keys, names=None):
        if not names:
            names = shell.default_vertex_attributes.keys()
        names = sorted(names)
        values = [shell.vertex[keys[0]][name] for name in names]
        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != shell.vertex[key][name]:
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
                        shell.set_vertex_attribute(key, name, value)

            return True
        return False

    @staticmethod
    def update_edge_attributes(shell, keys, names=None):
        if not names:
            names = shell.default_edge_attributes.keys()
        names = sorted(names)

        key = keys[0]
        values = shell.get_edge_attributes(key, names)

        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != shell.get_edge_attribute(key, name):
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
                        shell.set_edge_attribute(key, name, value)

            return True
        return False

    @staticmethod
    def update_face_attributes(shell, keys, names=None):
        if not names:
            names = shell.default_face_attributes.keys()
        names = sorted(names)

        key = keys[0]
        values = shell.get_face_attributes(key, names)

        if len(keys) > 1:
            for i, name in enumerate(names):
                for key in keys[1:]:
                    if values[i] != shell.get_face_attribute(key, name):
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
                        shell.set_face_attribute(key, name, value)

            return True
        return False


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
