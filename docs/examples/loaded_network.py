import numpy as np

from compas_fd.solvers import fd_numpy

result = fd_numpy(
    vertices=[[0, 0, 0], [0, 0, 0], [4, 0, 0]],
    fixed=[1, 2],
    edges=[(0, 1), (0, 2)],
    forcedensities=[1, 3],
    loads=[[0, 0, -4], [0, 0, 0], [0, 0, 0]],
)
np.testing.assert_allclose(result.vertices[0], [3, 0, -1], rtol=0, atol=1e-12)
print(result.vertices[0])
