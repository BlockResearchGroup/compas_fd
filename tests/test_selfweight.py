import numpy as np
import pytest
from compas.datastructures import Mesh
from compas_fd.loads import SelfweightCalculator


@pytest.fixture
def meshgrid() -> Mesh:
    mesh = Mesh.from_meshgrid(dx=10, nx=10)
    mesh.update_default_vertex_attributes(t=1.0)
    return mesh


def test_selfweight_meshgrid(meshgrid: Mesh) -> None:
    density = 1
    calculator = SelfweightCalculator(meshgrid, density=density)
    selfweight = calculator(meshgrid.vertices_attributes("xyz"))

    assert selfweight.shape[0] == meshgrid.number_of_vertices()
    assert selfweight[0] == 0.25 * meshgrid.vertex_attribute(0, "t") * density

    for vertex in meshgrid.vertices():
        t = meshgrid.vertex_attribute(vertex, "t")

        if meshgrid.vertex_degree(vertex) == 2:
            area = 0.25
        elif meshgrid.vertex_degree(vertex) == 3:
            area = 0.50
        else:
            area = 1.00

        assert selfweight[vertex] == area * t * density


def test_face_matrix_is_sparse_and_normalized(meshgrid: Mesh) -> None:
    calculator = SelfweightCalculator(meshgrid)

    assert calculator.F.shape == (meshgrid.number_of_faces(), meshgrid.number_of_vertices())
    assert calculator.F.format == "csr"
    row_sums = np.asarray(calculator.F.sum(axis=1)).ravel()  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    np.testing.assert_allclose(row_sums, 1.0)
