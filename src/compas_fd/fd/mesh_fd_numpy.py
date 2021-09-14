from numpy import array
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_fd.loads import SelfweightCalculator


def mesh_fd_numpy(mesh):
    """Find the equilibrium shape of a mesh for the given force densities.

    Parameters
    ----------
    mesh : compas_fd.datastructures.CableMesh
        The mesh to equilibriate.

    Returns
    -------
    None
        The function updates the input mesh and returns nothing.

    """
    k_i = mesh.key_index()
    fixed = mesh.vertices_where({'is_anchor': True})
    fixed = [k_i[key] for key in fixed]
    free = list(set(range(mesh.number_of_vertices())) - set(fixed))
    xyz = array(mesh.vertices_attributes('xyz'), dtype=float64)
    p = array(mesh.vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in mesh.edges_where({'is_edge': True})]
    q = array([attr['q'] for key, attr in mesh.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))

    density = mesh.attributes['density']

    calculate_sw = SelfweightCalculator(mesh, density=density)

    # replace by fd_numpy

    for key, attr in mesh.vertices(True):
        index = k_i[key]
        attr['x'] = xyz[index, 0]
        attr['y'] = xyz[index, 1]
        attr['z'] = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]

    for index, (key, attr) in enumerate(mesh.edges_where({'is_edge': True}, True)):
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]
