#ifndef FD_SOLVERS
#define FD_SOLVERS


// One-shot equilibrium calculation by the force density method.
std::tuple<Md3, Md3, Md1, Md1>
fd_solve(
	vvd& vertex_coordinates,
	vi& fixed_vertices,
	vvi& edges,
	vd& force_densities,
	vvd& loads);

#endif  // FD_SOLVERS