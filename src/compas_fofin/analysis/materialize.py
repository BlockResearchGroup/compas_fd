from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sqrt


__all__ = [
    'mesh_materialize_cables',
]


def mesh_materialize_cables(mesh, maxstress, E, safety, cables=None):
    """Materialize the edges of the data structure as individual cable segments.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The data structure.
    maxstress : float
        The maximum stress in the cables. The value should be provided in ``MPa``.
        For example, ``600``.
    E : float
        The E-modulus of the cables. The value should be provided in ``GPa``.
        For example, ``72.5``.
    safety : float
        The safety factor that should be applied to the forces.
        For example, ``1.5``.

    """
    if not maxstress:
        maxstress = 400

    if not E:
        E = 72.5

    if not safety:
        safety = 1.5

    if not cables:
        cables = {
            '6': {'A': 15.774},
            '8': {'A': 29.141}
        }

    for u, v, attr in mesh.edges_where({'is_edge': True}, True):
        f = attr['f']

        f_factored_N = safety * f * 1e3
        S_factored_N_m2 = pi * maxstress * 1e6

        r = sqrt(f_factored_N / S_factored_N_m2) * 1e3

        if r <= 3.0:
            size = '6'
        elif r <= 4.0:
            size = '8'
        # elif r <= 5.0:
        #     size = '10'
        # elif r <= 6.0:
        #     size = '12'
        # elif r <= 7.0:
        #     size = '14'
        # elif r <= 8.0:
        #     size = '16'
        # elif r <= 9.0:
        #     size = '18'
        # elif r <= 10.0:
        #     size = '20'
        else:
            Exception('Section not available')

        if size == '6':
            A = cables['6']['A']
            r = (A / 3.14159) ** 0.5
            x = f / (E * A)

        elif size == '8':
            A = cables['8']['A']
            r = (A / 3.14159) ** 0.5
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
