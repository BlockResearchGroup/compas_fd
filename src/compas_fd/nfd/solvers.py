from __future__ import annotations

from typing import Sequence
from typing_extensions import Annotated

from functools import partial

from numpy import array, average
from numpy.linalg import norm
from scipy.sparse.linalg import spsolve

from compas.datastructures import Mesh
from compas_fd.fd.result import Result

from .geometry import NaturalFace, NaturalEdge, Goals, mesh_preprocess
from .matrices import StiffnessMatrixAssembler, LoadMatrixAssembler


Vec = Annotated[Sequence[float], 3]


__all__ = [
    'nfd_ur_numpy',
    'nfd_numpy'
]


# =================================================
# solver iterators
# =================================================

def nfd_ur_numpy(mesh: Mesh, fixed: Sequence[int], stress_goals: Sequence[float] = None,
                 force_goals: Sequence[float] = None, force_density_goals: Sequence[float] = None,
                 vertex_loads: Sequence[Vec] = None, global_face_loads: Sequence[Vec] = None,
                 local_face_loads: Sequence[Vec] = None, stress_flag: int = 1, stress_ref: Vec = None,
                 stress_tol: float = 1e-2, xyz_tol: float = 1e-2, kmax: int = 10) -> Result:
    """Natural force density method with updated reference strategy.
    Input stress fields are taken for the reference geometry
    that is updated at each iteration by the natural force densities.

    Parameters
    ----------
    mesh : :class:`Mesh`
        Instance of Mesh datastructure.
    fixed: sequence of int
        Incices of fixed (anchored) vertices.
    stress_goals : sequence of sequence of float
        Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field per face,
        as input over reference directions and normalized over thickness.
        (default is None, setting a uniform stress field (1, 1, 0)).
    force_goals : sequence of float
        Goal force per edge (default is None).
    force_density_goals : sequence of float
        Goal force density per edge, overwrites force goals (default is None).
    vertex_loads : sequence of sequence of float
        Global XYZ components of loads per vertex (default is None).
    global_face_loads : sequence of sequence of float
        Global XYZ components of loads per face area (default is None).
    local_face_loads : sequence of sequence of float
        Local face frame XYZ components of loads per face area (default is None).
    stress_flag : {0, 1, 2, 3}
        Flag for stress calculation at final solver iteration (default is 1).
        0: Do not calculate stresses.
        1: Cauchy stresses per face.
        2: Principal stress values and vectors per face.
        3: Principal stress values and vectors in global frame.
    stress_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation.
    stress_tol : float
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
        XYZ vertex coordinates of the equilibrium geometry.
    ndarray
        Residual and reaction forces per vertex.
    tuple
        Stresses as (stress values, eigenvectors).
        Content depends on the value passed to the stress_flag parameter.
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
    goals = Goals(mesh, stress_goals, force_goals, force_density_goals, stress_ref)
    xyz, edges, faces = mesh_preprocess(mesh, goals)
    loads = LoadMatrixAssembler(xyz.shape[0], faces, vertex_loads,
                                global_face_loads, local_face_loads)

    if kmax == 1:
        return _nfd_solve(xyz, fixed, faces, edges, loads, stress_flag)

    for k in range(kmax):
        _xyz, r, f, lg, s = _nfd_solve(xyz, fixed, faces, edges, loads, -1)
        stress_goals = NaturalFace.get_stress_goals(faces)
        stress_res = average(norm(stress_goals - s.amplitudes, axis=1))
        xyz_Δ = max(norm(xyz - _xyz, axis=1))
        converged = (stress_res < stress_tol) or (xyz_Δ < xyz_tol)
        xyz = _xyz
        if converged:
            break

    _output_message(converged, k, stress_res, xyz_Δ)
    s = NaturalFace.get_stresses(faces, stress_flag)

    return Result(xyz, r, f, lg, s)


def _output_message(converged: bool, k: int, stress_res: float, xyz_Δ: float) -> None:
    if converged:
        print(f'Convergence reached after {k+1} iterations.')
    else:
        print(f'No convergence reached after {k+1} iterations.',
              '\nAverage stress residual:   ', round(stress_res, 5),
              '\nMax displacement residual: ', round(xyz_Δ, 5))


nfd_numpy = partial(nfd_ur_numpy, kmax=1)


# =================================================
# solver
# =================================================

def _nfd_solve(xyz, fixed: Sequence[int], faces: Sequence[NaturalFace],
               edges: Sequence[NaturalEdge], loads: Sequence[Vec], stress_flag: int) -> Result:
    """Solve system for coordinates and dependent variables
    using the one-shot natural force density method."""
    # pre-process vertex data
    v = xyz.shape[0]
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
    r = p - D.dot(xyz)
    f = NaturalEdge.get_forces(edges)
    lg = NaturalEdge.get_lengths(edges)
    s = NaturalFace.get_stresses(faces, stress_flag)

    return Result(_xyz, r, f, lg, s)
