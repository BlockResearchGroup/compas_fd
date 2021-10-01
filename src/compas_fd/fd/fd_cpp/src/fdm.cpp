#include "compas.h"
#include "fd_solvers.h"


void init_fd_solvers(py::module&);

PYBIND11_MODULE(fdm, m)
{
    m.doc() = "force density algorithms using Eigen.";
    init_fd_solvers(m);
}