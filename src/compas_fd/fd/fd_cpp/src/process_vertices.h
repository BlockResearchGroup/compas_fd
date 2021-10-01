#ifndef PROCESS_VERTICES
#define PROCESS_VERTICES

#include "compas.h"


// Set the indices of all free vertices.
// free vertices are defined in-place as output parameters.
void
set_free_vertices(
    const int& vertex_count,
    const int& edge_count,
    const vi& fixed_vertices,
    vi& free_vertices);


#endif  // PROCESS_VERTICES