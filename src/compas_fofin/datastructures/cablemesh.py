from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.geometry import angle_vectors


__all__ = ['CableMesh']


class CableMesh(Mesh):
    """The FF CableMesh.

    Attributes
    ----------
    default_vertex_attributes : dict
        The default attributes of all vertices of the CableMesh.

        * ``px (float)``: Component along the X axis of an applied point load. Default is ``0.0``.
        * ``py (float)``: Component along the Y axis of an applied point load. Default is ``0.0``.
        * ``pz (float)``: Component along the Z axis of an applied point load. Default is ``0.0``.

        * ``is_anchor (bool)``: Indicates whether a vertex is anchored and can take reaction forces. Default is ``False``.
        * ``is_fixed (bool)``:  Indicates whether a vertex is fixed furing geometric operations. Default is ``False``.
        * ``t (float)``:        Thickness of the concrete shell at the vertex. Default is ``0.05``.
        * ``constraint (int)``: Can be used to store the key of a geometrical object to which a vertex is constrained. Default is ``None``.
        * ``param (float)``:    Stores the current parameter of a vertex on the constraint object. Default is ``None``.

    default_edge_attributes : dict
        The default data attributes assigned to every new edge.

        * ``q (float)``:        Force density, edge force over stressed length. Default is ``1.0``.
        * ``f (float)``:        Force in the edge. Default is ``None``.
        * ``l (float)``:        Stressed length. Default is ``None``.
        * ``l0 (float)``:       Unstressed initial length. Default is ``None``.
        * ``E (float)``:        Young's modulus of elasticity. Default is ``None``.
        * ``radius (float)``:   Radius of the edge's cross section. Default is ``None``.
        * ``yield (float)``:    Yield strength. Default is ``None``.

    attributes : dict
        The default data attributes generally assigned to the CableMesh.

        * ``density (float)``:  Density of the concrete. Default is ``None``.


    Default vertex/edge/face attributes can be "public" or "protected".
    Protected attributes are usually only for internal use and should only be modified by the algorithms that rely on them.
    If you do change them, do so with care.

    Notes
    -----
    The CableMesh is implemented as a mesh.
    This means that it can only be used to model surface-like structures.
    """

    def __init__(self):
        super(CableMesh, self).__init__()
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'px': 0.0,
            'py': 0.0,
            'pz': 0.0,

            '_rx': 0.0,
            '_ry': 0.0,
            '_rz': 0.0,

            'is_anchor': False,
            'is_fixed': False,
            'constraint': None,
            'param': None,
            't': 0.05
        })

        self.default_edge_attributes.update({
            'q': 1.0,
            'f': None,
            'l': None,
            'l0': None,
            'E': None,
            'radius': None,
            'yield': None,

            '_is_edge': True
        })
        self.default_face_attributes.update({
            '_is_loaded': True
        })
        self.attributes.update({
            'name': 'CableMesh',
            'density': None
        })

    def vertices_on_edge_loop(self, uv):
        edges = self.edge_loop(uv)
        if len(edges) == 1:
            return edges[0]
        vertices = [edge[0] for edge in edges]
        if edges[-1][1] != edges[0][0]:
            vertices.append(edges[-1][1])
        return vertices

    def corner_vertices(self, tol=160):
        vkeys = []
        for key in self.vertices_on_boundary():
            if self.vertex_degree(key) == 2:
                vkeys.append(key)
            else:
                nbrs = []
                for nkey in self.vertex_neighbors(key):
                    if self.is_edge_on_boundary(key, nkey):
                        nbrs.append(nkey)
                u = (self.edge_vector(key, nbrs[0]))
                v = (self.edge_vector(key, nbrs[1]))
                if angle_vectors(u, v, deg=True) < tol:
                    vkeys.append(key)
        return vkeys
