from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys
from functools import partial
from math import pi

import compas
import compas_rhino

from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors
from compas.geometry import length_vector_sqrd
from compas.utilities import i_to_rgb

from compas_rhino.artists import MeshArtist

if compas.IPY:
    import System
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc


__all__ = ['ShellArtist']


class ShellArtist(MeshArtist):

    @property
    def shell(self):
        return self.datastructure

    @shell.setter
    def shell(self, shell):
        self.datastructure = shell

    def clear(self):
        super(ShellArtist, self).clear()
        self.clear_forces()
        self.clear_reactions()
        self.clear_residuals()
        self.clear_loads()

    def clear_(self, name):
        guids = compas_rhino.get_objects(name="{}.{}.*".format(self.shell.name, name))
        compas_rhino.delete_objects(guids)

    def clear_forces(self):
        self.clear_('force')

    def clear_reactions(self):
        self.clear_('reaction')

    def clear_residuals(self):
        self.clear_('residual')

    def clear_loads(self):
        self.clear_('load')

    def _draw_lines(self, lines):
        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=True)

    def _draw_cylinders(self, cylinders):
        compas_rhino.draw_cylinders(cylinders, layer=self.layer, clear=False, redraw=True, cap=True)

    def _draw_spheres(self, spheres):
        compas_rhino.draw_spheres(spheres, layer=self.layer, clear=False, redraw=True)

    # ==========================================================================
    # geometry
    # ==========================================================================

    # ==========================================================================
    # statics
    # ==========================================================================

    def draw_forces(self, compression=None, tension=None, scale=None):
        self.clear_forces()

        compression = compression or self.shell.attributes['color.forces:compression']
        tension = tension or self.shell.attributes['color.forces:tension']
        scale = scale or self.shell.attributes['scale.forces']

        tol = self.shell.attributes['tol.forces']
        tol2 = tol**2

        lines = []
        for u, v in self.shell.edges():
            f = self.shell.get_edge_attribute((u, v), 'f')
            sp, ep = self.shell.edge_coordinates(u, v)

            if f ** 2 < tol2:
                continue

            if f > 0.0:
                color = tension

            if f < 0.0:
                color = compression
                f = -f

            radius = scale * f

            lines.append({
                'start'  : sp,
                'end'    : ep,
                'radius' : radius,
                'color'  : color,
                'name'   : "{}.force.{}-{}".format(self.shell.name, u, v)
            })

        self._draw_cylinders(lines)

    def draw_reactions(self, color=None, scale=None):
        self.clear_reactions()

        color = color or self.shell.attributes['color.reactions']
        scale = scale or self.shell.attributes['scale.reactions']

        tol = self.shell.attributes['tol.reactions']
        tol2 = tol**2

        lines = []
        for key, attr in self.shell.vertices(True):
            if not attr['is_anchor']:
                continue

            r = rx, ry, rz = self.shell.get_vertex_attributes(key, ('rx', 'ry', 'rz'))

            if length_vector_sqrd(r) <= tol2:
                continue

            sp = x, y, z = self.shell.vertex_coordinates(key)
            ep = x - scale * rx, y - scale * ry, z - scale * rz

            lines.append({
                'start' : sp,
                'end'   : ep,
                'name'  : "{}.reaction.{}".format(self.shell.name, key),
                'color' : color,
                'arrow' : 'end'
            })

        self._draw_lines(lines)

    def draw_residuals(self, color=None, scale=None):
        self.clear_residuals()

        color = color or self.shell.attributes['color.residuals']
        scale = scale or self.shell.attributes['scale.residuals']

        tol = self.shell.attributes['tol.residuals']
        tol2 = tol**2

        lines = []
        for key, attr in self.shell.vertices(True):
            if attr['is_anchor']:
                continue

            r = rx, ry, rz = self.shell.get_vertex_attributes(key, ('rx', 'ry', 'rz'))

            if length_vector_sqrd(r) <= tol2:
                continue

            sp = x, y, z = self.shell.vertex_coordinates(key)
            ep = x + scale * rx, y + scale * ry, z + scale * rz

            lines.append({
                'start' : sp,
                'end'   : ep,
                'name'  : "{}.residual.{}".format(self.shell.name, key),
                'color' : color,
                'arrow' : 'end'
            })

        self._draw_lines(lines)

    def draw_loads(self, color=None, scale=None):
        self.clear_loads()

        color = color or self.shell.attributes['color.loads']
        scale = scale or self.shell.attributes['scale.loads']

        lines = []
        for key, attr in self.shell.vertices(True):
            if attr['is_anchor']:
                continue

            px, py, pz = self.shell.get_vertex_attributes(key, ('px', 'py', 'pz'))
            sp = x, y, z = self.shell.vertex_coordinates(key)
            ep = x + scale * px, y + scale * py, z + scale * pz

            lines.append({
                'start' : sp,
                'end'   : ep,
                'name'  : "{}.load.{}".format(self.shell.name, key),
                'color' : color,
                'arrow' : 'end'
            })

        self._draw_lines(lines)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
