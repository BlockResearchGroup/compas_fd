from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh


class CableMesh(Mesh):
    """Extension of the mesh datastructure with attributes and methods related to form finding of tensile surface structures.

    Parameters
    ----------
    name : str, optional
        The name of the cable mesh.

    Attributes
    ----------
    constraints : dict[str(guid), :class:`compas_fd.constraints.Constraint`]
        The constraints of the mesh.
    density : float
        The density used when computing the self-weight of the mesh.

    """

    DATASCHEMA = {}

    @property
    def __data__(self):
        raise NotImplementedError

    @classmethod
    def __from_data__(cls, data):
        raise NotImplementedError

    def __init__(self, name=None):
        super(CableMesh, self).__init__(name=name)
        self.attributes.update({"density": 1.0})
        self.constraints = {}
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

    @property
    def density(self):
        return self.attributes["density"]

    @density.setter
    def density(self, density):
        self.attributes["density"] = density

    def anchors(self):
        """Return the anchor vertices of the mesh.

        Returns
        -------
        list[int]
            The anchor vertices.

        """
        return list(self.vertices_where(is_anchor=True))

    def set_anchors(self, vertices):
        """Set specific vertices as anchors.

        Parameters
        ----------
        vertices : list[int]
            The vertices to set as anchors.

        Returns
        -------
        None

        """
        self.vertices_attribute("is_anchor", True, vertices)

    def fixed(self):
        """Return the fixed vertices of the mesh.

        Returns
        -------
        list[int]
            The fixed vertices.

        """
        return list(self.vertices_where(is_fixed=True))

    def set_fixed(self, vertices):
        """Set specific vertices as fixed.

        Parameters
        ----------
        vertices : list[int]
            The vertices to set as fixed.

        Returns
        -------
        None

        """
        self.vertices_attribute("is_fixed", True, vertices)

    def update_vertices(self, result):
        """Update the vertex attributes with the results of the form finding.

        Parameters
        ----------
        result : :class:`compas_fd.solvers.Result`
            The result of the form finding.

        Returns
        -------
        None

        """
        for key, attr in self.vertices(True):
            attr["x"] = result.vertices[key, 0]
            attr["y"] = result.vertices[key, 1]
            attr["z"] = result.vertices[key, 2]
            attr["_rx"] = result.residuals[key, 0]
            attr["_ry"] = result.residuals[key, 1]
            attr["_rz"] = result.residuals[key, 2]

    def edges(self):
        """Return the structural edges of the mesh.

        Returns
        -------
        list[tuple[int, int]]
            The structural edges.

        """
        return list(self.edges_where(_is_edge=True))

    def update_edges(self, result):
        """Update the edge attributes with the results of the form finding.

        Parameters
        ----------
        result : :class:`compas_fd.solvers.Result`
            The result of the form finding.

        Returns
        -------
        None

        """
        for index, edge in enumerate(self.edges()):
            self.edge_attribute(edge, "_f", result.forces[index, 0])
            self.edge_attribute(edge, "_l", result.lengths[index, 0])

    def set_vertex_constraint(self, vertex, constraint):
        """Set a constraint for a specific vertex.

        Parameters
        ----------
        vertex : int
            The vertex to set the constraint for.
        constraint : :class:`compas_fd.constraints.Constraint`
            The constraint.

        Returns
        -------
        None

        """
        self.vertex_attribute(vertex, "constraint", str(constraint.guid))
        self.vertex_attribute(vertex, "is_fixed", True)
        self.constraints[str(constraint.guid)] = constraint
