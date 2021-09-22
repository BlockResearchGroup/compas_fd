from functools import partial

from numpy import array, asarray, average, shape
from numpy.linalg import norm
from scipy.sparse.linalg import spsolve

from .geometry import NaturalFace, NaturalEdge, Goals, mesh_preprocess
from .matrices import StiffnessMatrixAssembler, LoadMatrixAssembler


__all__ = [
    'nfd_ur_numpy',
    'nfd_numpy'
]


# =================================================
# solver iterators
# =================================================

def nfd_ur_numpy(mesh, stress_goals=None, fd_goals=None, force_goals=None,
                 vertex_loads=None, global_face_loads=None, local_face_loads=None,
                 s_calc=1, s_ref=None, s_tol=1e-2, xyz_tol=1e-2, kmax=10):
    """Natural force density method with updated reference strategy.
    Input stress fields are taken for the reference geometry
    that is updated at each iteration by the natural force densities.

    Parameters
    ----------
    mesh : :class:`Mesh`
        Instance of Mesh datastructure.
    stress_goals : sequence of tuple
        Goal second Piola-Kirchhoff (σx, σy, τxy) stress field per face,
        as input over local directions and normalized over thickness
        (default is None, setting a uniform stress field (1, 1, 0)).
    fd_goals : sequence of float
        Goal force density per edge, overwrites force goals (default is None).
    force_goals : sequence of float
        Goal force per edge (default is None).
    vertex_loads : sequence of tuple
        Global XYZ components of loads per vertex (default is None).
    global_face_loads : sequence of tuple
        Global XYZ components of loads per face area (default is None).
    local_face_loads : sequence of tuple
        Local face frame XYZ components of loads per face area (default is None).
    s_calc : {0, 1, 2, 3}
        Flag for stress calculation at final solver iteration (default is 1).
        0: Do not calculate stresses.
        1: Calculate second Piola-Kirchhoff stresses per face.
        2: Calculate principal stress values and vectors per face.
        3: Calculate principal stress values and vectors in global frame.
    s_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation.
    s_tol : float
        Tolerance for averaged sum of squared errors
        from stress vectors to goal stress vector (default is 1e-2).
    xyz_tol : float
        Tolerance for difference in coordinate displacements
        between two consecutive iterations (default is 1e-2).
    kmax : int
        Maximum number of iterations (default is 10).

    Returns
    ----------
    ndarray
        XYZ coordinates of the equilibrium geometry.
    ndarray
        Residual and reaction forces per vertex.
    tuple
        Tuple as (stresses, eigenvectors).
        Exact content of tuple depends on the value given to s_calc parameter.
    list
        Forces per edge.

    Notes
    -----
    For more info, see [1]_, [2]_

    References
    ----------
    .. [1] Pauletti, R.M.O. and Pimenta, P.M., 2008. The natural force
           density method for the shape finding of taut structures.
           Computer Methods in Applied Mechanics and Engineering,
           197(49-50), pp.4419-4428.

    .. [2] Pauletti, R.M.O. and Fernandes, F.L., 2020. An outline of the natural
           force density method and its extension to quadrilateral elements.
           International Journal of Solids and Structures, 185, pp.423-438.
    """
    # pre-process mesh data
    goals = Goals(mesh, stress_goals, fd_goals, force_goals, s_ref)
    faces, edges, vertices, fixed = mesh_preprocess(mesh, goals)
    loads = LoadMatrixAssembler(vertices, faces, vertex_loads,
                                global_face_loads, local_face_loads)
    xyz = asarray(vertices)

    if kmax == 1:
        return _nfd_solve(xyz, fixed, faces, edges, loads, s_calc)

    for k in range(kmax):
        _xyz, r, s, f = _nfd_solve(xyz, fixed, faces, edges, loads, -1)
        s_goals = NaturalFace.get_stress_goals(faces)
        s_res = average(norm(s_goals - s.amplitudes, axis=1))
        xyz_Δ = max(norm(xyz - _xyz, axis=1))
        converged = (s_res < s_tol) or (xyz_Δ < xyz_tol)
        xyz = _xyz
        if converged:
            break

    _output_message(converged, k, s_res, xyz_Δ)
    s = NaturalFace.get_stresses(faces, xyz, s_calc)

    return xyz, r, s, f


def _output_message(converged, k, s_res, xyz_Δ):
    if converged:
        print(f'Convergence reached after {k+1} iterations.')
    else:
        print(f'No convergence reached after {k+1} iterations.',
              '\nAverage stress residual:   ', round(s_res, 5),
              '\nMax displacement residual: ', round(xyz_Δ, 5))


nfd_numpy = partial(nfd_ur_numpy, kmax=1)


# =================================================
# solver
# =================================================

def _nfd_solve(xyz, fixed, faces, edges, loads, s_calc):
    """Solve system for coordinates and dependent variables
    using the one-shot natural force density method."""
    # pre-process vertex data
    v = shape(xyz)[0]
    free = list(set(range(v)) - set(fixed))
    _xyz = array(xyz, copy=True)

    # assemble new stiffness matrix
    sma = StiffnessMatrixAssembler(free, fixed, edges, faces)
    D, Di, Df = sma.matrix, sma.free_matrix, sma.fixed_matrix

    # get updated load matrix
    loads.update()
    p = loads.matrix

    # solve for coordinates and update elements
    _xyz[free] = spsolve(Di, p[free] - Df.dot(xyz[fixed]))
    for face in faces:
        face.update_xyz(_xyz)
    for edge in edges:
        edge.update_xyz(_xyz)

    # solve for dependent variables
    s = NaturalFace.get_stresses(faces, _xyz, s_calc)
    f = NaturalEdge.get_forces(edges, _xyz)
    r = p - D.dot(xyz)

    return _xyz, r, s, f
