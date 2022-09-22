from numpy import array
from numpy import asarray
from numpy import float64

from compas_fd.loads import SelfweightCalculator
from compas_fd.fd.fd_constrained_numpy import fd_constrained_numpy
from compas_fd.datastructures import CableMesh


def mesh_fd_constrained_numpy(
    mesh: CableMesh,
    kmax: int = 100,
    damping: float = 0.1,
    tol_res: float = 1e-3,
    tol_disp: float = 1e-3,
) -> CableMesh:
    """
    Iteratively find the equilibrium shape of a mesh for the given force densities.

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
    vertices = array(mesh.vertices_attributes("xyz"), dtype=float64)
    fixed = [v_i[v] for v in mesh.vertices_where({"is_anchor": True})]
    edges = list(mesh.edges_where(_is_edge=True))
    qs = asarray(mesh.edges_attribute("q", keys=edges), dtype=float64).reshape((-1, 1))
    loads = array(mesh.vertices_attributes(("px", "py", "pz")), dtype=float64)
    constraints = list(mesh.vertices_attribute("constraint"))
    selfweight = SelfweightCalculator(
        mesh,
        density=mesh.attributes["density"],
        thickness_attr_name="t",
    )

    ij = [(v_i[u], v_i[v]) for u, v in edges]

    result = fd_constrained_numpy(
        vertices=vertices,
        fixed=fixed,
        edges=ij,
        forcedensities=qs,
        loads=loads,
        constraints=constraints,
        kmax=kmax,
        tol_res=tol_res,
        tol_disp=tol_disp,
        damping=damping,
        selfweight=selfweight,
    )

    _update_mesh(mesh, result)
    return mesh


def _update_mesh(mesh, result):
    vertex_index = mesh.vertex_index()
    for vertex, attr in mesh.vertices(True):
        index = vertex_index[vertex]
        attr["x"] = result.vertices[index, 0]
        attr["y"] = result.vertices[index, 1]
        attr["z"] = result.vertices[index, 2]
        attr["_rx"] = result.residuals[index, 0]
        attr["_ry"] = result.residuals[index, 1]
        attr["_rz"] = result.residuals[index, 2]

    for index, (edge, attr) in enumerate(mesh.edges_where({"_is_edge": True}, True)):
        attr["_f"] = result.forces[index, 0]
        attr["_l"] = result.lenghts[index, 0]
