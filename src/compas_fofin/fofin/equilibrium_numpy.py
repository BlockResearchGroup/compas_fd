from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import array
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import connectivity_matrix
from compas.numerical import normrow

from compas_fofin.loads import SelfweightCalculator


__all__ = ['update_xyz_numpy']


def update_xyz_numpy(mesh):
    """Find the equilibrium shape of a mesh for the given force densities.

    Parameters
    ----------
    mesh : compas_fofin.datastructures.Cablenet
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

    if density:
        sw = calculate_sw(xyz)
        p[:, 2] = -sw[:, 0]

    C = connectivity_matrix(edges, 'csr')
    Ci = C[:, free]
    Cf = C[:, fixed]
    Ct = C.transpose()
    Cit = Ci.transpose()
    Q = diags([q.flatten()], [0])
    A = Cit.dot(Q).dot(Ci)
    b = p[free] - Cit.dot(Q).dot(Cf).dot(xyz[fixed])

    xyz[free] = spsolve(A, b)

    if density:
        sw = calculate_sw(xyz)
        p[:, 2] = -sw[:, 0]

    l = normrow(C.dot(xyz))
    f = q * l
    r = p - Ct.dot(Q).dot(C).dot(xyz)

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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
