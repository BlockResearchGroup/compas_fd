from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi

from compas.datastructures import Mesh


__all__ = ['Cablenet']


class Cablenet(Mesh):
    """:class:`Cablenet` extends the mesh datastructure
    with attributes and methods related to form finding (and analysis) of
    flexible cablenet formwork for concrete shells.

    Attributes
    ----------
    default_vertex_attributes : dict
        The default data attributes assigned to every new vertex.

        .. code-block:: python

            {
                'px' : 0.0,            # X-component of an externally applied load.
                'py' : 0.0,            # Y-component of an externally applied load.
                'pz' : 0.0,            # Z-component of an externally applied load.
                'rx' : 0.0,            # X-component of an unbalanced (residual) force.
                'ry' : 0.0,            # Y-component of an unbalanced (residual) force.
                'rz' : 0.0,            # Z-component of an unbalanced (residual) force.
                't' : 0.0,             # Thickness of the shell.
                'is_anchor' : False,   # Indicate that a vertex is anchored and can take reaction forces in XYZ.
                'is_fixed' : False,    # Can be used to mark a vertex as "fixed" during geometrical operations such as smoothing.
                'constraint' : None,   # Can be used to store the name or ID of a geometrical object to which a vertex is constrained.
                'param' : None,        # Stores the current parameter of a vertex on the constraint object.
            }

    default_edge_attributes : dict
        The default data attributes assigned to every new edge.

        .. code-block:: python

            {
                'q' : 0.0,
                'f' : 0.0,
                'l' : 0.0,
                'E' : 0.0,
                'r' : 0.0,
                'l0' : 0.0,
            }

    Notes
    -----
    The cablenet is implemented as a mesh.
    This means that it can only be used to model surface-like structures.

    """

    def __init__(self):
        super(Cablenet, self).__init__()
        self.attributes.update({
            'density': 14.0,
        })
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'px': 0.0,
            'py': 0.0,
            'pz': 0.0,
            'rx': 0.0,
            'ry': 0.0,
            'rz': 0.0,
            't': 0.05,
            'is_anchor': False,
            'is_fixed': False,
            'constraint': None,
            'param': None,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'f': 0.0,
            'l': 0.0,
            'E': 210.0,
            'r': 0.0,
            'l0': 0.0,
            'is_edge': True,
            'yield': 235.0,
        })
        self.default_face_attributes.update({
            'strip': None
        })

    @classmethod
    def from_rhinomesh(cls, guid):
        """Make a cable net from a Rhino mesh.

        Parameters
        ----------
        guid : str
            The GUID of the Rhino mesh.

        Returns
        -------
        :class:`Cablenet`
            An instance of a cable net.

        """
        from compas_rhino.geometry import RhinoMesh
        return RhinoMesh.from_guid(guid).to_compas(cls=cls)

    @classmethod
    def from_rhinosurface(cls, guid, u=20, v=10):
        """Make a cable net from a Rhino surface.

        Parameters
        ----------
        guid : str
            The GUID of the Rhino surface.
        u : int (10)
            The number of isolines in the "u" direction.
            Default is `10`.
        v : int (10)
            The number of isolines in the "v" direction.
            Default is `10`.

        Returns
        -------
        :class:`Cablenet`
            An instance of a cable net.

        """
        from compas_rhino.geometry import RhinoSurface
        return RhinoSurface.from_guid(guid).uv_to_compas(cls=cls, density=(u, v))

    def get_continuous_edges(self, edge, aligned=False):
        """Get the edges forming a continuous line with the selected edge.

        Parameters
        ----------
        edge : tuple
            The identifier of the starting edge.
        aligned : bool (False)
            Return the edges aligned with the starting edge.

        Returns
        -------
        list
            If ``aligned == True``, vertex pairs directed such that they form
            a continuous chain with the orientation of the starting edge.

            If ``aligned == False`` (default), vertex pairs directed
            as they are in the data structure.

        Examples
        --------
        Get any edge, not on the boundary as starting edge.
        >>> edges = cablenet.get_continuous_edges(start, aligned=True)
        >>> all(cablenet.has_edge(u, v, directed=False) for u, v in edges)
        True
        >>> edges = cablenet.get_continuous_edges(start, aligned=False)
        >>> all(cablenet.has_edge(u, v, directed=False) for u, v in edges)
        True
        >>> edges = cablenet.get_continuous_edges(start, aligned=False)
        >>> all(cablenet.has_edge(u, v, directed=True) for u, v in edges)
        True
        >>> edges = cablenet.get_continuous_edges(start, aligned=True)
        >>> all(cablenet.has_edge(u, v, directed=True) for u, v in edges)
        False

        """
        boundary = set(self.vertices_on_boundary())
        edges = []
        v, u = edge
        end = u
        while True:
            edges.append((v, u))
            if v == end:
                break
            if v in boundary:
                break
            if self.vertex_degree(v) != 4:
                break
            nbrs = self.vertex_neighbors(v, ordered=True)
            i = nbrs.index(u)
            u = nbrs[i - 2]
            u, v = v, u
        edges[:] = edges[::-1]
        u, v = edge
        end = u
        while True:
            if v == end:
                break
            if v in boundary:
                break
            if self.vertex_degree(v) != 4:
                break
            nbrs = self.vertex_neighbors(v, ordered=True)
            i = nbrs.index(u)
            u = nbrs[i - 2]
            u, v = v, u
            edges.append((u, v))
        if aligned:
            return edges
        edgeset = set(list(self.edges()))
        return [(u, v) if (u, v) in edgeset else (v, u) for u, v in edges]

    def get_parallel_edges(self, edge, aligned=False):
        """Get the edges parallel to the selected edge.

        Parameters
        ----------
        edge : tuple
            Pair of vertex identifiers.
        aligned : bool (False)
            Return the edges aligned with the starting edge.

        Returns
        -------
        list
            Identifiers of edges, as vertex pairs, parallel to the starting edge.

        Examples
        --------
        >>>

        """
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
            edges.append((v, u))
        if aligned:
            return edges
        directed = set(list(self.edges()))
        return [(u, v) if (u, v) in directed else (v, u) for u, v in edges]

    def get_face_strip(self, edge):
        """Get the face strip defined by an edge.

        Parameters
        ----------
        edge : tuple
            Pair of vertex identifiers.

        Returns
        -------
        list
            Identifiers of faces.

        Examples
        --------
        >>>

        """
        edges = self.get_parallel_edges(edge, aligned=True)
        faces = []
        seen = set()
        for u, v in edges:
            left = self.halfedge[u][v]
            right = self.halfedge[v][u]
            if left is not None:
                if left not in seen:
                    faces.append(left)
                    seen.add(left)
            if right is not None:
                if right not in seen:
                    faces.append(right)
                    seen.add(right)
        return faces

    def draw(self, layer=None, clear_layer=True, settings=None):
        from compas_fofin.rhino import CablenetArtist
        layer = layer or settings.get('layer')
        artist = CablenetArtist(self, layer=layer)
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
        if settings.get('show.normals', False):
            artist.draw_normals(scale=settings.get('scale.normals'))
        if settings.get('show.forces', False):
            artist.draw_forces(compression=settings.get('color.forces:compression', None),
                               tension=settings.get('color.forces:tension', None),
                               scale=settings.get('scale.forces', None))
        if settings.get('show.reactions', False):
            artist.draw_reactions(color=settings.get('color.reactions', None),
                                  scale=settings.get('scale.reactions', None))
        if settings.get('show.residuals', False):
            artist.draw_residuals(color=settings.get('color.residuals', None),
                                  scale=settings.get('scale.residuals', None),
                                  tol=settings.get('tol.residuals', None))
        if settings.get('show.loads', False):
            artist.draw_loads(color=settings.get('color.loads', None),
                              scale=settings.get('scale.loads', None))
        if settings.get('show.selfweight', False):
            artist.draw_selfweight(color=settings.get('color.selfweight', None),
                                   scale=settings.get('scale.selfweight', None))
        if settings.get('show.stress', False):
            artist.draw_stress(scale=settings.get('scale.stress', None))
        artist.redraw()

    def residual(self, key):
        return self.vertex_attributes(key, ('rx', 'ry', 'rz'))

    def stress(self, key):
        radius = self.edge_attribute(key, 'r')
        area = pi * radius ** 2
        force = 1e3 * self.edge_attribute(key, 'f')
        return 1e-6 * force / area

    def strain(self, key):
        l = self.edge_attribute(key, 'l')
        l0 = self.edge_attribute(key, 'l0')
        return l / l0


# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":

    import doctest
    import random
    import compas

    FILE = compas.get('quadmesh.obj')
    cablenet = Cablenet.from_obj(FILE)
    start = random.choice(list(set(cablenet.edges()) - set(cablenet.edges_on_boundary())))

    doctest.testmod(globs=globals())
