from numpy import array
from numpy import float64

from compas_fd.loads import SelfweightCalculator
from compas_fd.datastructures import CableMesh
from .fd_numpy import fd_numpy


def mesh_fd_numpy(mesh: CableMesh) -> CableMesh:
    """
    Find the equilibrium shape of a mesh for the given force densities.

    Parameters
    ----------
    mesh : :class:`compas_fd.datastructures.CableMesh`
        The mesh to equilibriate.

    Returns
    -------
    :class:`compas_fd.datastructures.CableMesh`
        The function updates the mesh in place,
        but returns a reference to the updated mesh as well
        for compatibility with RPCs.

    """
    v_i = mesh.vertex_index()
    fixed = mesh.vertices_where(is_anchor=True)
    fixed = [v_i[key] for key in fixed]
    xyz = array(mesh.vertices_attributes("xyz"), dtype=float64)
    p = array(mesh.vertices_attributes(("px", "py", "pz")), dtype=float64)
    edges = [(v_i[u], v_i[v]) for u, v in mesh.edges_where(_is_edge=True)]
    q = array(
        mesh.edges_attribute("q", keys=mesh.edges_where(_is_edge=True)),
        dtype=float64,
    ).reshape((-1, 1))
    density = mesh.attributes["density"]

    calculate_sw = SelfweightCalculator(mesh, density=density)
    p[:, 2] -= calculate_sw(xyz)[:, 0]

    result = fd_numpy(vertices=xyz, fixed=fixed, edges=edges, forcedensities=q, loads=p)

    for key, attr in mesh.vertices(True):
        index = v_i[key]
        attr["x"] = result.vertices[index, 0]
        attr["y"] = result.vertices[index, 1]
        attr["z"] = result.vertices[index, 2]
        attr["_rx"] = result.residuals[index, 0]
        attr["_ry"] = result.residuals[index, 1]
        attr["_rz"] = result.residuals[index, 2]

    for index, (key, attr) in enumerate(mesh.edges_where(_is_edge=True, data=True)):
        attr["_f"] = result.forces[index, 0]
        attr["_l"] = result.lengths[index, 0]

    return mesh