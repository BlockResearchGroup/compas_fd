from numpy import array, asarray
from numpy import float64

import compas_fd
from .fd_constrained_numpy import fd_constrained_numpy


def mesh_fd_constrained_numpy(mesh: 'compas_fd.datastructures.CableMesh',
                              kmax: int = 100,
                              damping: float = 0.1,
                              tol_res: float = 1e-3,
                              tol_disp: float = 1e-3) -> 'compas_fd.datastructures.CableMesh':
    """Iteratively find the equilibrium shape of a mesh for the given force densities.

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
    vertices = array(mesh.vertices_attributes('xyz'), dtype=float64)
    fixed = [v_i[v] for v in mesh.vertices_where({'is_anchor': True})]
    edges = [(v_i[u], v_i[v]) for u, v in mesh.edges_where({'_is_edge': True})]
    forcedensities = asarray([attr['q'] for edge, attr in mesh.edges_where({'_is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    loads = array(mesh.vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    constraints = list(mesh.vertices_attribute('constraint'))

    result = fd_constrained_numpy(vertices=vertices,
                                  fixed=fixed,
                                  edges=edges,
                                  forcedensities=forcedensities,
                                  loads=loads,
                                  constraints=constraints,
                                  kmax=kmax,
                                  tol_res=tol_res,
                                  tol_disp=tol_disp,
                                  damping=damping)

    _update_mesh(mesh, result)

    return mesh


def _update_mesh(mesh, result):
    vertex_index = mesh.vertex_index()
    for vertex, attr in mesh.vertices(True):
        index = vertex_index[vertex]
        attr['x'] = result.vertices[index, 0]
        attr['y'] = result.vertices[index, 1]
        attr['z'] = result.vertices[index, 2]
        attr['_rx'] = result.residuals[index, 0]
        attr['_ry'] = result.residuals[index, 1]
        attr['_rz'] = result.residuals[index, 2]

    for index, (vertex, attr) in enumerate(mesh.edges_where({'_is_edge': True}, True)):
        attr['_f'] = result.forces[index, 0]
        attr['_l'] = result.lenghts[index, 0]
