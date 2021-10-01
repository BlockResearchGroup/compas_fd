#ifndef CONNECTIVITY_MATRICES
#define CONNECTIVITY_MATRICES

#include "compas.h"


// Construct the connectivity matrices of a connected graph.
// Coefficient (i, j) equals 1 if edge i starts at vertex i,
// -1 if edge i ends at vertex j, and 0 otherwise.
// Matrices are defined in-place as output parameters:
// full matrix C, free vertices matrix Ci, fixed vertices matrix Cf.
void
set_connectivity_matrices(
    const vvi& edges,
    const vi& free_vertices,
    const vi& fixed_vertices,
    SMd& C, SMd& Ci, SMd& Cf);


#endif  // CONNECTIVITY_MATRICES