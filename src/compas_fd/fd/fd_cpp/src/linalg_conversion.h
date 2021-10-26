#ifndef LINALG_CONVERSION
#define LINALG_CONVERSION

#include "compas.h"


// Construct a generic Eigen::Vector from an std::vector.
// The same data memory address is referenced, no copy is made.
template <typename T> Eigen::Map<Eigen::Vector<double, Eigen::Dynamic>>&
matrix_from_vec1d(
    std::vector<T>& vec)
{
    Eigen::Map<Eigen::Vector<T, Eigen::Dynamic>> out_vec(vec.data(), vec.size());
    return out_vec;
}


// Construct a generic row-major Eigen::MatrixX3 from a nested std::vector.
// A new contiguous slot of memory is allocated for the Eigen::Matrix.
template <typename T> Eigen::Matrix<T, Eigen::Dynamic, 3>
matrixX3_from_vec2d(
    const std::vector<std::vector<T>>& vec)
{
    int row_count = vec.size();
    Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic> out_mat(vec.size(), 3);
    for (unsigned int i = 0; i < vec.size(); ++i)
        out_mat.row(i) = Eigen::Vector<T, Eigen::Dynamic>::Map(vec[i].data(), 3);
    return out_mat;
}


// Construct a generic std::vector from an Eigen::Vector.
// A new slot of memory is allocated for the std::vector.
template <typename T> std::vector<T>
matrix_to_vec1d(
    const Eigen::Vector<T, Eigen::Dynamic>& mat)
{
    return std::vector<T>(&mat[0], mat.data() + mat.cols() * mat.rows());
}


// Construct a nested std::vector from an Eigen::Matrix of 3 columns.
// A new slot of memory is allocated for the std::vector.
template <typename T> std::vector<std::array<T, 3>>
matrixX3_to_vec2d(
    const Eigen::Matrix<T, Eigen::Dynamic, 3>& mat)
{
    std::vector<std::array<T, 3>> out_vec;
    out_vec.resize(mat.rows());
    Eigen::Matrix<T, Eigen::Dynamic, 3, Eigen::RowMajor>::Map(
        out_vec[0].data(), mat.rows(), mat.cols()) = mat;
    return out_vec;
}


#endif  // LINALG_CONVERSION