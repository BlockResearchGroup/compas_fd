from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import sqrt


__all__ = ['mesh_materialize_cables']


def mesh_materialize_cables(mesh, safety_forces=1.0, safety_material=1.0):
    """Materialize the edges of the data structure as individual cable segments.

    Parameters
    ----------
    mesh : compas.datastructures.Mesh
        The data structure.
    safety_forces : float (1.0)
        The safety factor that should be applied to the forces.
        The forces are multiplied by the provided factor.
        Default is ``1.0``.
    safety_material : float (1.0)
        The safety factor that should be applied to the yield stress of the material.
        The yield stress is divided by the provided factor.
        Default is ``1.0``.

    """
    for key, attr in mesh.edges_where({'is_edge': True}, True):
        u, v = key
        f = attr['f']
        yieldstress = attr['yield']
        E = attr['E']

        f_factored_N = safety_forces * f * 1e3
        S_factored_N_m2 = pi * safety_material * yieldstress * 1e6

        r = sqrt(f_factored_N / S_factored_N_m2) * 1e3

        if r <= 2.0:
            r = 2.0
        elif r <= 3.0:
            r = 3.0
        elif r <= 4.0:
            r = 4.0
        elif r <= 5.0:
            r = 5.0
        elif r <= 6.0:
            r = 6.0
        elif r <= 7.0:
            r = 7.0
        elif r <= 8.0:
            r = 8.0
        elif r <= 9.0:
            r = 9.0
        elif r <= 10.0:
            r = 10.0
        else:
            Exception('Section not available')

        A = pi * r ** 2
        x = f / (E * A)

        l = mesh.edge_length(u, v)
        l0 = l / (1 + x)

        attr['r'] = r * 1e-3
        attr['l0'] = l0


def mesh_unstressed_lengths(mesh):
    for u, v, attr in mesh.edges_where({'is_edge': True}, True):
        f = attr['f']
        # yieldstress = attr['yield']
        E = attr['E']
        r = attr['r']
        r *= 1e3
        A = pi * r ** 2
        x = f / (E * A)
        l = mesh.edge_length(u, v)
        l0 = l / (1 + x)
        attr['l0'] = l0


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
