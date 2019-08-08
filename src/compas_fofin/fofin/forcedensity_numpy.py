from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from cvxpy import *

from numpy import array
from numpy import float64
from numpy import zeros_like
from numpy import atleast_2d
from numpy import asarray
from numpy import sum
from numpy import absolute
from numpy import where
from numpy import inf

from scipy.sparse import vstack
from scipy.sparse import diags

from scipy.linalg import norm
from scipy.linalg import cho_solve
from scipy.linalg import cho_factor
from scipy.linalg import solve
from scipy.linalg import lstsq

from compas.numerical import normrow
from compas.numerical import connectivity_matrix
from compas.numerical import devo_numpy

from compas_fofin.loads import SelfweightCalculator


__all__ = [
    'find_q_numpy',
]


def find_q_numpy(mesh, qmin=0.001, qmax=1000):
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
    Cit   = Ci.transpose()
    # ==========================================================================
    # preprocess
    # ==========================================================================
    calculate_sw = SelfweightCalculator(mesh, density=mesh.attributes['density'])
    # ==========================================================================
    # solver
    # ==========================================================================
    sw = calculate_sw(xyz)

    p[:, 2] = - sw[:, 0]

    pi = p[free]
    pi = pi.reshape((-1, 1), order='F')

    U = diags([C.dot(xyz[:, 0])], [0])
    V = diags([C.dot(xyz[:, 1])], [0])
    W = diags([C.dot(xyz[:, 2])], [0])

    A = vstack((
        Cit.dot(U),
        Cit.dot(V),
        Cit.dot(W)
    ))

    q = Variable((A.shape[1], 1))

    objective = Minimize(sum_squares(A * q - pi))
    constraints = [qmin <= q, q <= qmax]

    prob = Problem(objective, constraints)

    prob.solve(verbose=False, solver='CPLEX')

    q = array(q.value.ravel()).reshape((-1, 1))
    # ==========================================================================
    # residuals
    # ==========================================================================
    l = normrow(C.dot(xyz))
    f = q * l
    Q = diags([q.ravel()], [0])
    r = p - Ct.dot(Q).dot(C).dot(xyz)
    # ==========================================================================
    # update
    # ==========================================================================
    for index, (key, attr) in enumerate(mesh.vertices(True)):
        attr['rx'] = r[index, 0]
        attr['ry'] = r[index, 1]
        attr['rz'] = r[index, 2]
        attr['sw'] = p[index, 2]
    for index, (u, v, attr) in enumerate(mesh.edges_where({'is_edge': True}, True)):
        attr['q'] = q[index, 0]
        attr['f'] = f[index, 0]
        attr['l'] = l[index, 0]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    pass
