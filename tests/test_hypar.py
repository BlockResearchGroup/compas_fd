import numpy as np
from compas_fd.solvers import fd_numpy


def test_hypar():
    o = [0, 0, 0]
    a = [0, 0, 1]
    b = [1, 0, 0]
    c = [1, 1, 1]
    d = [0, 1, 0]
    vertices = [o, a, b, c, d]
    edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
    forcedensities = [1, 1, 1, 1]
    result = fd_numpy(
        vertices=vertices,
        fixed=[1, 2, 3, 4],
        edges=edges,
        forcedensities=forcedensities,
    )
    assert np.allclose(result.vertices[0], [0.5, 0.5, 0.5])
