#include "compas.h"
#include "fd_solvers.h"
#include "process_vertices.h"
#include "connectivity_matrices.h"
#include "linalg_conversion.h"


std::tuple<Md3, Md3, Md1, Md1>
fd_solve(
    vvd& vertex_coordinates,
    vi& fixed_vertices,
    vvi& edges,
    vd& force_densities,
    vvd& loads)
{
    // pre-process vertex indices arrays
    int vertex_count = vertex_coordinates.size();
    int edge_count = edges.size();
    vi free_vertices;
    set_free_vertices(vertex_count, edge_count,
                      fixed_vertices, free_vertices);

    // set primary data matrices
    Md3 X = matrixX3_from_vec2d(vertex_coordinates);
    Md3 P = matrixX3_from_vec2d(loads);
    auto& q = matrix_from_vec1d(force_densities);
    DMd Q = q.asDiagonal();

    // set connectivity matrices
    SMd C(edge_count, vertex_count);
    SMd Ci(edge_count, free_vertices.size());
    SMd Cf(edge_count, fixed_vertices.size());
    set_connectivity_matrices(edges, free_vertices, fixed_vertices, C, Ci, Cf);

    // solve for current force densities
    // build stiffness matrices
    SMd Cit = Ci.transpose();
    SMd D = C.transpose() * Q * C;
    SMd Di = Cit * Q * Ci;
    SMd Df = Cit * Q * Cf;

    // solve for free coordinates
    Md b = P(free_vertices, Eigen::all) - (Df * X(fixed_vertices, Eigen::all));
    Eigen::SimplicialLDLT<SMd> solver;
    solver.compute(Di);
    if (solver.info() != Eigen::Success)
        throw std::exception("Singular stiffness matrix");
    Md3 X_free = solver.solve(b);                   // updated free vertex coordinates
    for (unsigned int i = 0; i < X_free.rows(); ++i)
        X.row(free_vertices[i]) = X_free.row(i);

    // get dependent variables
    Md3 R = P - (D * X);                            // residuals and reactions
    Md1 L = (C * X).rowwise().norm();               // edge lengths
    Md1 F = Q.diagonal().array() * L.array();       // edge forces

    return {X, R, F, L};
}


void init_fd_solvers(py::module& m)
{
    m.def("fd_solve",
          &fd_solve,
          py::arg("vertex_coordinates").noconvert(),
          py::arg("fixed_vertices").noconvert(),
          py::arg("edges").noconvert(),
          py::arg("force_densities").noconvert(),
          py::arg("loads").noconvert());
};