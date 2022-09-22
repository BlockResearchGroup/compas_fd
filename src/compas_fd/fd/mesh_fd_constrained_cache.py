from typing import Callable
from typing import List
from typing import Tuple
from typing_extensions import Literal
from nptyping import NDArray
from nptyping import Float64

from numpy import array
from numpy import asarray
from numpy import float64

from compas_fd.loads import SelfweightCalculator
from compas_fd.fd.fd_numerical_data import FDNumericalData
from compas_fd.datastructures import CableMesh

from compas_fd.fd.fd_constrained_numpy import _solve_fd
from compas_fd.fd.fd_constrained_numpy import _update_constraints
from compas_fd.fd.fd_constrained_numpy import _is_converged_residuals
from compas_fd.fd.fd_constrained_numpy import _is_converged_disp


CACHE = None


class CacheError(Exception):
    pass


def mesh_fd_constrained_cache_create(
    mesh: CableMesh,
    edgeset: List[Tuple[int, int]],
    kmax: int = 10,
    damping: float = 0.1,
    tol_res: float = 1e-3,
    tol_disp: float = 1e-3,
) -> None:

    v_i = mesh.vertex_index()
    vertices = array(mesh.vertices_attributes("xyz"), dtype=float64)
    fixed = [v_i[v] for v in mesh.vertices_where(is_anchor=True)]
    edges = list(mesh.edges_where(_is_edge=True))
    qs = asarray(mesh.edges_attribute("q", keys=edges), dtype=float64).reshape((-1, 1))
    loads = array(mesh.vertices_attributes(("px", "py", "pz")), dtype=float64)
    constraints = list(mesh.vertices_attribute("constraint"))
    selfweight = SelfweightCalculator(
        mesh,
        density=mesh.attributes["density"],
        thickness_attr_name="t",
    )

    uv_index = {(u, v): index for index, (u, v) in enumerate(edges)}
    uv_index.update({(v, u): index for index, (u, v) in enumerate(edges)})

    edgeset = [uv_index[u, v] for u, v in edgeset]

    ij = [(v_i[u], v_i[v]) for u, v in edges]
    numdata = FDNumericalData.from_params(vertices, fixed, ij, qs, loads)

    cache_data = {
        "numdata": numdata,
        "edgeset": edgeset,
        "qs": qs.copy(),
        "constraints": constraints,
        "selfweight": selfweight,
        "kmax": kmax,
        "damping": damping,
        "tol_res": tol_res,
        "tol_disp": tol_disp,
    }
    return cache_data


def mesh_fd_constrained_cache_delete() -> None:
    pass


def mesh_fd_constrained_cache_call(
    scale: float, cached_data: dict
) -> List[List[float]]:

    numdata: FDNumericalData = cached_data["numdata"]
    edgeset: List[int] = cached_data["edgeset"]
    qs: NDArray[Literal["*, 1"], Float64] = cached_data["qs"]
    kmax: int = cached_data["kmax"]
    damping: float = cached_data["damping"]
    selfweight: Callable = cached_data["selfweight"]
    constraints = cached_data["constraints"]
    tol_res: float = cached_data["tol_res"]
    tol_disp: float = cached_data["tol_disp"]

    numdata.update_forcedensities(edgeset, scale * qs[edgeset])

    for k in range(kmax):
        xyz_prev = numdata.xyz
        _solve_fd(numdata, selfweight)
        _update_constraints(numdata, constraints, damping)

        if _is_converged_residuals(
            numdata.tangent_residuals, tol_res
        ) and _is_converged_disp(xyz_prev, numdata.xyz, tol_disp):
            break

    return numdata.xyz.tolist()
