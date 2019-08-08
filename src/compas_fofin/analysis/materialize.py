from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sqrt


__all__ = [
    'mesh_materialize_cables',
]


def mesh_materialize_cables(mesh, maxstress=None, E=None, safety=None):
    """Materialize the edges of the data structure as individual cable segments.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The data structure.
    maxstress : float (400.0)
        The maximum stress in the cables. The value should be provided in ``MPa``.
    E : float (72.5)
        The E-modulus of the cables. The value should be provided in ``GPa``.
    safety : float (1.5)
        The safety factor that should be applied to the forces.

    """
    if not maxstress:
        maxstress = 400

    if not E:
        E = 72.5

    if not safety:
        safety = 1.5

    for u, v, attr in mesh.edges_where({'is_edge': True}, True):
        f = attr['f']

        f_factored_N = safety * f * 1e3
        S_factored_N_m2 = pi * maxstress * 1e6

        r = sqrt(f_factored_N / S_factored_N_m2) * 1e3

        if r <= 3.0:
            size = '6'
            r = 3.0
        elif r <= 4.0:
            size = '8'
            r = 4.0
        elif r <= 5.0:
            size = '10'
            r = 5.0
        elif r <= 6.0:
            size = '12'
            r = 6.0
        elif r <= 7.0:
            size = '14'
            r = 7.0
        elif r <= 8.0:
            size = '16'
            r = 8.0
        elif r <= 9.0:
            size = '18'
            r = 9.0
        elif r <= 10.0:
            size = '20'
            r = 10.0
        else:
            Exception('Section not available')

        A = pi * r ** 2
        x = f / (E * A)

        l  = mesh.edge_length(u, v)
        l0 = l / (1 + x)

        attr['E'] = E
        attr['r'] = r * 1e-3
        attr['l0'] = l0
        attr['size'] = size


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
