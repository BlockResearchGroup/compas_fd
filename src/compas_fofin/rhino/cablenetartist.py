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
from compas.utilities import Colormap

from compas_rhino.artists import MeshArtist

if compas.IPY:
    import System
    import Rhino
    import rhinoscriptsyntax as rs
    import scriptcontext as sc


__all__ = ['CablenetArtist']


class CablenetArtist(MeshArtist):
    """The :class:`CablenetArtist` provides functionality for visualisation of cablenet components in Rhino.

    Examples
    --------
    .. code-block:: python

        artist = CablenetArtist(cablenet, layer="Cablenet")
        artist.clear_layer()
        artist.draw_vertices()
        artist.draw_edges()
        artist.draw_faces()
        artist.draw_forces()
        artist.draw_reactions()
        artist.redraw()

    """

    def __init__(self, mesh, layer=None):
        super(MeshArtist, self).__init__(layer=layer)
        self.mesh = mesh
        self.defaults.update({
            'color.forces:compression': (0, 0, 255),
            'color.forces:tension': (255, 0, 0),
            'color.reactions': (0, 255, 0),
            'color.residuals': (0, 255, 255),
            'color.loads': (0, 0, 255),
            'color.selfweight': (255, 255, 255),
            'scale.forces': 0.1,
            'scale.reactions': 1.0,
            'scale.residuals': 1.0,
            'scale.loads': 1.0,
            'scale.selfweight': 1.0,
            'tol.reactions': 1e-3,
            'tol.residuals': 1e-3,
            'tol.forces': 1e-3})

    @property
    def cablenet(self):
        """:class:`compas_fofin.datastructures.Cablenet` : The cablenet datastructure."""
        return self.datastructure

    @cablenet.setter
    def cablenet(self, cablenet):
        self.datastructure = cablenet

    def clear(self):
        """Clear all components previously drawn by the artist."""
        super(CablenetArtist, self).clear()
        self.clear_forces()
        self.clear_reactions()
        self.clear_residuals()
        self.clear_loads()
        self.clear_selfweight()
        self.clear_stress()

    def clear_(self, name):
        guids = compas_rhino.get_objects(name="{}.{}.*".format(self.cablenet.name, name))
        compas_rhino.delete_objects(guids)

    def clear_forces(self):
        """Clear all internal forces drawn by the artist."""
        self.clear_('force')

    def clear_reactions(self):
        """Clear all reaction forces drawn by the artist."""
        self.clear_('reaction')

    def clear_residuals(self):
        """Clear all residual forces drawn by the artist."""
        self.clear_('residual')

    def clear_loads(self):
        """Clear all loads drawn by the artist."""
        self.clear_('load')

    def clear_selfweight(self):
        """Clear all selfweight drawn by the artist."""
        self.clear_('selfweight')

    def clear_stress(self):
        """Clear all stress drawn by the artist."""
        self.clear_('stress')

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
        """Draw the internal forces in the cablenet.

        Parameters
        ----------
        compression : color specification, optional
            The color of the compression forces.
            This defaults to the color set in the attributes of the cablenet.
            `self.defaults['color.forces:compression']`
        tension : color specification, optional
            The color of the tension forces.
            This defaults to the color set in the attributes of the cablenet.
            `self.defaults['color.forces:tension']`
        scale : float, optional
            The scale of the forces.
            This defaults to the scale set in the attributes of the cablenet.
            `self.defaults['scale.forces']`

        Notes
        -----
        The forces are drawn as cylinders around the edges of the cablenet datastructure.
        THe radius of the cylinder is proportional to the size of the force and scaled by
        the specified factor.
        If the radius is smaller than a specified tolerance, the drawing of the specific
        cylinder is skipped.

        """
        self.clear_forces()

        compression = compression or self.defaults['color.forces:compression']
        tension = tension or self.defaults['color.forces:tension']
        scale = scale or self.defaults['scale.forces']

        tol = self.defaults['tol.forces']
        tol2 = tol**2

        lines = []
        for u, v in self.cablenet.edges_where({'is_edge': True}):
            f = self.cablenet.get_edge_attribute((u, v), 'f')
            sp, ep = self.cablenet.edge_coordinates(u, v)

            if f ** 2 < tol2:
                continue

            if f > 0.0:
                color = tension

            if f < 0.0:
                color = compression
                f = -f

            radius = scale * f

            lines.append({
                'start': sp,
                'end': ep,
                'radius': radius,
                'color': color,
                'name': "{}.force.{}-{}".format(self.cablenet.name, u, v)
            })

        self._draw_cylinders(lines)

    def draw_reactions(self, color=None, scale=None):
        self.clear_reactions()

        color = color or self.defaults['color.reactions']
        scale = scale or self.defaults['scale.reactions']

        tol = self.defaults['tol.reactions']
        tol2 = tol**2

        lines = []
        for key, attr in self.cablenet.vertices(True):
            if not attr['is_anchor']:
                continue

            r = rx, ry, rz = self.cablenet.get_vertex_attributes(key, ('rx', 'ry', 'rz'))

            if length_vector_sqrd(r) <= tol2:
                continue

            sp = x, y, z = self.cablenet.vertex_coordinates(key)
            ep = x - scale * rx, y - scale * ry, z - scale * rz

            lines.append({
                'start': sp,
                'end': ep,
                'name': "{}.reaction.{}".format(self.cablenet.name, key),
                'color': color,
                'arrow': 'end'
            })

        self._draw_lines(lines)

    def draw_residuals(self, color=None, scale=None, tol=None):
        self.clear_residuals()

        color = color or self.defaults['color.residuals']
        scale = scale or self.defaults['scale.residuals']
        tol = tol or self.defaults['tol.residuals']
        tol2 = tol**2

        lines = []
        for key, attr in self.cablenet.vertices(True):
            if attr['is_anchor']:
                continue

            r = rx, ry, rz = self.cablenet.get_vertex_attributes(key, ('rx', 'ry', 'rz'))

            if length_vector_sqrd(r) <= tol2:
                continue

            sp = x, y, z = self.cablenet.vertex_coordinates(key)
            ep = x + scale * rx, y + scale * ry, z + scale * rz

            lines.append({
                'start': sp,
                'end': ep,
                'name': "{}.residual.{}".format(self.cablenet.name, key),
                'color': color,
                'arrow': 'end'
            })

        self._draw_lines(lines)

    def draw_loads(self, color=None, scale=None):
        self.clear_loads()

        color = color or self.defaults['color.loads']
        scale = scale or self.defaults['scale.loads']

        lines = []
        for key, attr in self.cablenet.vertices(True):
            if attr['is_anchor']:
                continue

            px, py, pz = self.cablenet.get_vertex_attributes(key, ('px', 'py', 'pz'))
            sp = x, y, z = self.cablenet.vertex_coordinates(key)
            ep = x + scale * px, y + scale * py, z + scale * pz

            lines.append({
                'start': sp,
                'end': ep,
                'name': "{}.load.{}".format(self.cablenet.name, key),
                'color': color,
                'arrow': 'end'
            })

        self._draw_lines(lines)

    def draw_selfweight(self, color=None, scale=None):
        self.clear_selfweight()

        color = color or self.defaults['color.selfweight']
        scale = scale or self.defaults['scale.selfweight']

        rho = self.cablenet.attributes['density']

        if not rho:
            return

        lines = []
        for key, attr in self.cablenet.vertices(True):
            if attr['is_anchor']:
                continue

            thickness = self.cablenet.get_vertex_attribute(key, 't')
            area = self.cablenet.vertex_area(key)
            volume = area * thickness
            weight = rho * volume
            sp = x, y, z = self.cablenet.vertex_coordinates(key)
            ep = x, y, z - scale * weight

            lines.append({
                'start': sp,
                'end': ep,
                'name': "{}.selfweight.{}".format(self.cablenet.name, key),
                'color': color,
                'arrow': 'end'
            })

        self._draw_lines(lines)

    def draw_stress(self, scale=None):
        self.clear_stress()

        scale = scale or self.defaults['scale.stress']

        stress = [self.cablenet.stress(key) for key in self.cablenet.edges_where({'is_edge': True})]
        cmap = Colormap(stress, 'rgb')

        lines = []
        for index, (u, v) in enumerate(self.cablenet.edges_where({'is_edge': True})):
            sp, ep = self.cablenet.edge_coordinates(u, v)

            lines.append({
                'start': sp,
                'end': ep,
                'radius': scale,
                'color': cmap(stress[index]),
                'name': "{}.stress.{}-{}".format(self.cablenet.name, u, v)
            })

        self._draw_cylinders(lines)



# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
