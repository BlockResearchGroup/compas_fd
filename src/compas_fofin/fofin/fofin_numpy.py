from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from numpy import array
from numpy import float64
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

from compas.numerical import normrow
from compas.numerical import connectivity_matrix

from compas_fofin.loads import SelfweightCalculator


__all__ = [
    'fofin_numpy'
]


def fofin_numpy(mesh):
    """Find the equilibrium shape of a mesh for the given force densities.
    """
    k_i   = mesh.key_index()
    fixed = mesh.vertices_where({'is_anchor': True})
    fixed = [k_i[key] for key in fixed]
    free  = list(set(range(mesh.number_of_vertices())) - set(fixed))
    xyz   = array(mesh.get_vertices_attributes('xyz'), dtype=float64)
    p     = array(mesh.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)
    edges = [(k_i[u], k_i[v]) for u, v in mesh.edges_where({'is_edge': True})]
    q     = array([attr['q'] for u, v, attr in mesh.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
    C     = connectivity_matrix(edges, 'csr')
    Ct    = C.transpose()
    Ci    = C[:, free]
    Cf    = C[:, fixed]
    Cit   = Ci.transpose()

    selfweight = SelfweightCalculator(mesh, density=mesh.attributes['density'], thickness_attr_name='t')
    sw = selfweight(xyz)
    p[:, 2] -= sw[:, 0]

    Q = diags([q.flatten()], [0])
    A = Cit.dot(Q).dot(Ci)
    b = p[free] - Cit.dot(Q).dot(Cf).dot(xyz[fixed])

    xyz[free] = spsolve(A, b)

    l = normrow(C.dot(xyz))
    f = q * l
    r = p - Ct.dot(Q).dot(C).dot(xyz)

    for key, attr in mesh.vertices(True):
        index = k_i[key]
        attr['x']  = xyz[index, 0]
        attr['y']  = xyz[index, 1]
        attr['z']  = xyz[index, 2]
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]

    for index, (u, v, attr) in enumerate(mesh.edges_where({'is_edge': True}, True)):
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
