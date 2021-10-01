#ifndef COMPAS
#define COMPAS

#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

#include <vector>
#include <tuple>
#include <numeric>
#include <exception>
#include <Eigen/Sparse>
#include <Eigen/SparseCholesky>


namespace py = pybind11;

using vi = std::vector<int>;
using vd = std::vector<double>;
using vvi = std::vector<std::vector<int>>;
using vvd = std::vector<std::vector<double>>;
using Md = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic>;
using Md3 = Eigen::Matrix<double, Eigen::Dynamic, 3>;
using Md1 = Eigen::Vector<double, Eigen::Dynamic>;
using DMd = Eigen::DiagonalMatrix<double, Eigen::Dynamic, Eigen::Dynamic>;
using SMd = Eigen::SparseMatrix<double>;


#endif // COMPAS