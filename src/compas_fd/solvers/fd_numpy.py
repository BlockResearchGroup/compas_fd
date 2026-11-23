from collections.abc import Sequence

from compas.linalg import normrow

from compas_fd._scipy import dot_coordinates
from compas_fd._scipy import solve_coordinates
from compas_fd.types import FloatNx3

from .fd_numerical_data import FDNumericalData
from .result import Result


def fd_numpy(
    *,
    vertices: FloatNx3,
    fixed: list[int],
    edges: Sequence[tuple[int, int]],
    forcedensities: Sequence[float],
    loads: FloatNx3 | None = None,
) -> Result:
    """Compute the equilibrium coordinates of a system of vertices connected by edges.

    Parameters
    ----------
    vertices : FloatNx3
        Initial XYZ coordinates in vertex-index order, shape `(n, 3)`.
    fixed : list[int]
        The fixed vertices.
    edges : list[tuple[int, int]]
        The edges between the vertices.
    forcedensities : list[float]
        Axial force per unit length for each edge, in edge order.
    loads : FloatNx3, optional
        Applied force vectors, shape `(n, 3)`. Defaults to zero.

    Returns
    -------
    Result
        Equilibrium coordinates and residual forces in vertex order, and
        axial forces and lengths in edge order.

    See Also
    --------
    fd_constrained_numpy

    Notes
    -----
    Coordinates and lengths use the same units. Loads, residuals and axial
    forces use a consistent force unit. A compatible float64 input coordinate
    array may be updated in place.

    Examples
    --------
    >>> from compas_fd.solvers import fd_numpy
    >>> result = fd_numpy(
    ...     vertices=[[0, 0, 0], [0, 0, 0], [4, 0, 0]],
    ...     fixed=[1, 2],
    ...     edges=[(0, 1), (0, 2)],
    ...     forcedensities=[1, 3],
    ...     loads=[[0, 0, -4], [0, 0, 0], [0, 0, 0]],
    ... )
    >>> result.vertices[0].tolist()
    [3.0, 0.0, -1.0]

    """
    numdata = FDNumericalData.from_params(vertices, fixed, edges, forcedensities, loads)

    xyz = numdata.xyz
    free = numdata.free
    fixed = numdata.fixed
    q = numdata.q
    p = numdata.p
    C = numdata.C
    A = numdata.A
    Ai = numdata.Ai
    Af = numdata.Af

    b = p[free] - dot_coordinates(Af, xyz[fixed])
    xyz[free] = solve_coordinates(Ai, b)
    lengths = normrow(dot_coordinates(C, xyz))
    forces = q * lengths
    residuals = p - dot_coordinates(A, xyz)

    return Result(xyz, residuals, forces, lengths)
