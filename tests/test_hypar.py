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
    assert result.residuals is not None
    assert result.forces is not None
    assert result.lengths is not None
    assert np.allclose(result.vertices[0], [0.5, 0.5, 0.5])
    assert np.allclose(result.lengths, np.sqrt(0.75))
    assert np.allclose(result.forces, result.lengths)
    assert np.allclose(result.residuals[0], [0.0, 0.0, 0.0])


def test_loaded_network_matches_linear_equilibrium():
    """Check the one-free-node form of Schek (1974), doi:10.1016/0045-7825(74)90045-0."""
    # With anchors A=(0, 0, 0), B=(4, 0, 0) and q=(1, 3),
    # equilibrium gives 4X = A + 3B + P. P=(0, 0, -4) yields X=(3, 0, -1).
    result = fd_numpy(
        vertices=[[0, 0, 0], [0, 0, 0], [4, 0, 0]],
        fixed=[1, 2],
        edges=[(0, 1), (0, 2)],
        forcedensities=[1, 3],
        loads=[[0, 0, -4], [0, 0, 0], [0, 0, 0]],
    )

    # This well-conditioned, small system needs only a float64 round-off allowance.
    assert result.residuals is not None
    assert result.forces is not None
    assert result.lengths is not None
    np.testing.assert_allclose(result.vertices, [[3, 0, -1], [0, 0, 0], [4, 0, 0]], rtol=0, atol=1e-12)
    np.testing.assert_allclose(result.residuals, [[0, 0, 0], [3, 0, -1], [-3, 0, -3]], rtol=0, atol=1e-12)
    np.testing.assert_allclose(result.lengths, [[np.sqrt(10)], [np.sqrt(2)]], rtol=0, atol=1e-12)
    np.testing.assert_allclose(result.forces, [[np.sqrt(10)], [3 * np.sqrt(2)]], rtol=0, atol=1e-12)
