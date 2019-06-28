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
            'name' : 'Shell',
            'density' : 1.0
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
            't' : 1.0,
            'is_anchor' : False,
            'is_fixed'  : False,
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
        self.default_face_attributes.updates({
            'strip' : None
        })
    
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
