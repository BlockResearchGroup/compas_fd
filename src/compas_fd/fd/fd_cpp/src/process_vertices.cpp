#include "compas.h"
#include "process_vertices.h"


void
set_free_vertices(
    const int& vertex_count,
    const int& edge_count,
    const vi& fixed_vertices,
    vi& free_vertices)
{
    vi all_vertices(vertex_count);
    std::iota(all_vertices.begin(), all_vertices.end(), 0);
    free_vertices.reserve(vertex_count - fixed_vertices.size());
    std::set_difference(all_vertices.begin(), all_vertices.end(),
        fixed_vertices.begin(), fixed_vertices.end(),
        std::inserter(free_vertices, free_vertices.begin()));
}