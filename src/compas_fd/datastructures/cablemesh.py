from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


class CableMesh(Mesh):
    """
    Extension of the mesh datastructure with attributes and methods related to form finding of tensile surface structures.
    """

    def __init__(self):
        super(CableMesh, self).__init__()
        self.attributes.update(
            {
                "density": 22.0,
            }
        )
        self.default_vertex_attributes.update(
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "px": 0.0,
                "py": 0.0,
                "pz": 0.0,
                "t": 0.0,
                "is_anchor": False,
                "is_fixed": False,
                "constraint": None,
                "param": None,
                "_rx": 0.0,
                "_ry": 0.0,
                "_rz": 0.0,
            }
        )
        self.default_edge_attributes.update(
            {
                "q": 1.0,
                "_is_edge": True,
                "_l": 0.0,
                "_f": 0.0,
                "_r": 0.0,
            }
        )
        self.default_face_attributes.update(
            {
                "is_loaded": True,
            }
        )
