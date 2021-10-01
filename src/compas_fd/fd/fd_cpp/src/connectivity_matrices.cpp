#include "compas.h"
#include "connectivity_matrices.h"


//aliases
using T = Eigen::Triplet<int>;

void
set_connectivity_matrices(
    const vvi& edges,
    const vi& free_vertices,
    const vi& fixed_vertices,
    SMd& C, SMd& Ci, SMd& Cf)
{
    std::vector<T> triplets, free_triplets, fixed_triplets;
    triplets.reserve(2 * edges.size());
    free_triplets.reserve(free_vertices.size());
    fixed_triplets.reserve(fixed_vertices.size());
    SMd Ci_mask(C.cols(), free_vertices.size());
    SMd Cf_mask(C.cols(), fixed_vertices.size());

    // full connectivity matrix
    for (unsigned int i = 0; i < edges.size(); ++i)
    {
        triplets.emplace_back(i, edges[i][0],  1);
        triplets.emplace_back(i, edges[i][1], -1);
    }
    C.setFromTriplets(triplets.begin(), triplets.end());

    // free vertices connectivity matrix
    for (unsigned int i = 0; i < free_vertices.size(); ++i)
        free_triplets.emplace_back(free_vertices[i], i, 1);
    Ci_mask.setFromTriplets(free_triplets.begin(), free_triplets.end());
    Ci = C * Ci_mask;

    // fixed vertices connectivity matrix
    for (unsigned int i = 0; i < fixed_vertices.size(); ++i)
        fixed_triplets.emplace_back(fixed_vertices[i], i, 1);
    Cf_mask.setFromTriplets(fixed_triplets.begin(), fixed_triplets.end());
    Cf = C * Cf_mask;
}