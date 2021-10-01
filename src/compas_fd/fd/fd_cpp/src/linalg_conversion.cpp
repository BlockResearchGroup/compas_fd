//#include "linalg_conversion.h"
//
//#include <vector>
//#include <Eigen/Sparse>
//
//
//template <typename T> Eigen::Vector<T, Eigen::Dynamic>
//matrix_from_vec1d(const std::vector<T>& vec)
//{
//    return Eigen::Map<const Eigen::Vector<T, Eigen::Dynamic>, Eigen::Unaligned>
//        (vec.data(), vec.size());
//}
//
//
//template <typename T> Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic>
//matrix_from_vec2d(const std::vector<std::vector<T>>& vec)
//{
//    Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic> mat(vec.size(), vec[0].size());
//    for (size_t i = 0; i < vec.size(); ++i)
//        mat.row(i) = Eigen::Vector<T, Eigen::Dynamic>::Map(&vec[i][0], vec[i].size());
//    return mat;
//}
//
//
//template <typename T> std::vector<T>
//matrix_to_vec1d(const Eigen::Vector<T, Eigen::Dynamic>& mat)
//{
//    return std::vector<T>(&mat[0], mat.data() + mat.cols() * mat.rows());
//}
//
//
//template <typename T> std::vector<std::vector<T>>
//matrix_to_vec2d(const Eigen::Matrix<T, Eigen::Dynamic, 3>& mat)
//{
//    std::vector<std::vector<T>> vec;
//    vec.reserve(mat.rows());
//    for (int i = 0; i < mat.rows(); ++i)
//    {
//        const T* begin = &mat.row(i).data()[0];
//        vec.push_back(std::vector<T>(begin, begin + mat.cols()));
//
//        //std::vector<T> in_vec = std::vector<T>(&mat[0], mat.data() + mat.cols() * mat.rows());
//        //vec.push_back(in_vec);
//    }
//    return vec;
//}
//
//
//
//template Eigen::Vector<T, Eigen::Dynamic> matrix_from_vec1d<double>();