from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from compas.datastructures import Mesh


class CableMesh(Mesh):
    """:class:`CableMesh` extends the mesh datastructure
    with attributes and methods related to form finding of tensile surface structures.
    """

    if not compas.IPY:
        from compas_fd.fd import mesh_fd_numpy
        from compas_fd.fd import mesh_fd_constrained_numpy
        fd_numpy = mesh_fd_numpy
        fd_constrained_numpy = mesh_fd_constrained_numpy

    def __init__(self):
        super(CableMesh, self).__init__()
        self.attributes.update({
            'density': 22.0,
        })
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'px': 0.0,
            'py': 0.0,
            'pz': 0.0,
            't': 0.0,
            'is_anchor': False,
            'is_fixed': False,
            'constraint': None,
            'param': None,
            '_rx': 0.0,
            '_ry': 0.0,
            '_rz': 0.0,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            '_is_edge': True,
            '_l': 0.0,
            '_f': 0.0,
            '_r': 0.0,
        })
        self.default_face_attributes.update({
            'is_loaded': True,
        })
