from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


class Shell(Mesh):
    """``Shell`` extends the ``Mesh`` datastructure
    with attributes and methods related to form finding and analysis of shells.
    """

    def __init__(self):
        super(Shell, self).__init__()
        self.attributes.update({
            'color.vertex'            : (0, 0, 0),
            'color.face'              : (255, 255, 255),
            'color.edge'              : (0, 0, 0),
            'color.force:compression' : (255, 0, 0),
            'color.force:tension'     : (255, 0, 0),
            'color.reaction'          : (0, 255, 0),
            'color.residual'          : (0, 255, 255),
            'color.load'              : (0, 0, 255),
            'scale.force'             : 0.1,
            'scale.reaction'          : 1.0,
            'scale.residual'          : 1.0,
            'scale.load'              : 1.0,
            'tol.reaction'            : 1e-3,
            'tol.residual'            : 1e-3,
            'tol.force'               : 1e-3,

            'density' : 0.0,
        })
        self.default_vertex_attributes.update({
            'x' : 0.0,
            'y' : 0.0,
            'z' : 0.0,
            'px' : 0.0,
            'py' : 0.0,
            'pz' : 0.0,
            'rx' : 0.0,
            'ry' : 0.0,
            'rz' : 0.0,
            't' : 0.0,
            'is_anchor' : False,
            'is_fixed'  : False,
            'constraint': None
        })
        self.default_edge_attributes.update({
            'is_edge' : True,
            'q' : 1.0,
            'f' : 0.0,
            'l' : 0.0,
            'E' : 0.0,
            'r' : 0.0,
            'l0' : 0.0,
        })
        self.default_face_attributes.update({
            'strip' : None
        })

    @classmethod
    def from_lines(cls, lines):
        """Make a shell from a Rhino mesh."""
        return super(Shell, None).from_lines(cls, lines, delete_boundary_face=True)

    @classmethod
    def from_rhinomesh(cls, guid):
        """Make a shell from a Rhino mesh."""
        from compas_rhino.helpers import mesh_from_guid
        return mesh_from_guid(cls, guid)

    @classmethod
    def from_rhinosurface(cls, guid):
        """Make a mesh from a Rhino surface."""
        from compas_rhino.helpers import mesh_from_surface
        return mesh_from_surface(cls, guid)

    def get_continuous_edges(self, edge):
        """Get the edges forming a continuous line with the selected edge."""
        boundary = set(self.vertices_on_boundary())
        edges = [edge]
        u, v = edge
        end = v
        while True:
            if self.vertex_degree(u) != 4:
                break
            if u == end:
                break
            if u in boundary:
                break
            nbrs = self.vertex_neighbors(u, ordered=True)
            i = nbrs.index(v)
            v = nbrs[i - 2]
            edges.append((u, v))
            u, v = v, u
        v, u = edge
        end = v
        while True:
            if self.vertex_degree(u) != 4:
                break
            if u == end:
                break
            if u in boundary:
                break
            nbrs = self.vertex_neighbors(u, ordered=True)
            i = nbrs.index(v)
            v = nbrs[i - 2]
            edges.append((u, v))
            u, v = v, u
        directed = set(list(self.edges()))
        return [(u, v) if (u, v) in directed else (v, u) for u, v in edges]

    def get_parallel_edges(self, edge):
        """Get the edges parallel to the selected edge."""
        edges = [edge]
        u, v = edge
        while True:
            face = self.halfedge[u][v]
            if face is None:
                break
            vertices = self.face_vertices(face)
            if len(vertices) != 4:
                break
            i = vertices.index(u)
            u = vertices[i - 1]
            v = vertices[i - 2]
            if u in edge and v in edge:
                break
            edges.append((u, v))
        edges[:] = edges[::-1]
        v, u = edge
        while True:
            face = self.halfedge[u][v]
            if face is None:
                break
            vertices = self.face_vertices(face)
            if len(vertices) != 4:
                break
            i = vertices.index(u)
            u = vertices[i - 1]
            v = vertices[i - 2]
            if u in edge and v in edge:
                break
            edges.append((u, v))
        directed = set(list(self.edges()))
        return [(u, v) if (u, v) in directed else (v, u) for u, v in edges]

    def draw(self, layer=None, clear_layer=True, settings=None):
        from compas_fofin.rhino import ShellArtist
        layer = layer or settings.get('layer')
        artist = ShellArtist(self, layer=layer)
        if clear_layer:
            artist.clear_layer()
        if settings.get('show.vertices', True):
            vertexcolor = {}
            vertexcolor.update({key: (0, 255, 0) for key in self.vertices_where_predicate(lambda key, attr: attr['constraint'] is not None)})
            vertexcolor.update({key: (255, 0, 0) for key in self.vertices_where({'is_anchor': True})})
            artist.draw_vertices(color=vertexcolor)
        if settings.get('show.edges', True):
            artist.draw_edges()
        if settings.get('show.faces', True):
            artist.draw_faces()
        if settings.get('show.forces', False):
            artist.draw_forces(
                compression=settings.get('color.force:compression', None),
                tension=settings.get('color.force:compression', None),
                scale=settings.get('scale.force', None))
        if settings.get('show.reactions', False):
            artist.draw_reactions(
                color=settings.get('color.reaction', None),
                scale=settings.get('scale.reaction', None))
        if settings.get('show.residuals', False):
            artist.draw_reactions(
                color=settings.get('color.residual', None),
                scale=settings.get('scale.residual', None))
        if settings.get('show.loads', False):
            artist.draw_loads(
                color=settings.get('color.load', None),
                scale=settings.get('scale.load', None))
        artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
