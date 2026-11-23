"""Typed interfaces for the specific SciPy operations used by FD."""

from typing import cast

from scipy.linalg import norm  # pyright: ignore[reportUnknownVariableType]
from scipy.sparse import csc_matrix
from scipy.sparse import csr_matrix
from scipy.sparse import dia_matrix
from scipy.sparse import diags  # pyright: ignore[reportUnknownVariableType]
from scipy.sparse.linalg import spsolve  # pyright: ignore[reportUnknownVariableType]

from compas_fd.types import FloatArray


def dot_coordinates(matrix: csr_matrix | csc_matrix, coordinates: FloatArray) -> FloatArray:
    """Multiply a sparse matrix by a dense coordinate array."""
    return cast(FloatArray, matrix.dot(coordinates))  # pyright: ignore[reportUnknownMemberType]


def weighted_product(left: csr_matrix, weights: dia_matrix, right: csr_matrix) -> csc_matrix:
    """Form the sparse product left.T * weights * right."""
    return cast(csc_matrix, left.T.dot(weights).dot(right))  # pyright: ignore[reportUnknownMemberType]


def diagonal(values: FloatArray) -> dia_matrix:
    """Construct a sparse matrix with the given main diagonal."""
    return cast(dia_matrix, diags([values.flatten()], [0]))  # pyright: ignore[reportArgumentType]


def solve_coordinates(matrix: csc_matrix, right_hand_side: FloatArray) -> FloatArray:
    """Solve a sparse linear system with a dense coordinate right-hand side."""
    return cast(FloatArray, spsolve(matrix, right_hand_side))


def row_lengths(coordinates: FloatArray) -> FloatArray:
    """Return the Euclidean length of each row as a one-dimensional array."""
    return cast(FloatArray, norm(coordinates, axis=1))
