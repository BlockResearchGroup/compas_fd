from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh

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
            '_is_loaded': True,
            'placeholder': True
        })
        self.attributes.update({
            'name': 'CableMesh',
            'density': None
        })
