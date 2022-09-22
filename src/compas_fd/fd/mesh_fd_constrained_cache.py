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
from compas_fd.fd.fd_constrained_numpy import _post_process_fd


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

    global CACHE

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
    ij = [(v_i[u], v_i[v]) for u, v in edges]
    numdata = FDNumericalData.from_params(vertices, fixed, ij, qs, loads)
    edgeset = [uv_index[u, v] for u, v in edgeset]

    cache_data = {
        "numdata": numdata,
        "edgeset": edgeset,
        "qs": qs,
        "constraints": constraints,
        "selfweight": selfweight,
        "kmax": kmax,
        "damping": damping,
        "tol_res": tol_res,
        "tol_disp": tol_disp,
    }
    CACHE = cache_data


def mesh_fd_constrained_cache_delete() -> None:
    global CACHE
    CACHE = None


def mesh_fd_constrained_cache_call(scale: float) -> List[List[float]]:
    global CACHE

    numdata: FDNumericalData = CACHE["numdata"]
    edgeset: List[int] = CACHE["edgeset"]
    qs: NDArray[Literal["*, 1"], Float64] = CACHE["qs"]
    kmax: int = CACHE["kmax"]
    damping: float = CACHE["damping"]
    selfweight: Callable = CACHE["selfweight"]
    constraints = CACHE["constraints"]
    tol_res: float = CACHE["tol_res"]
    tol_disp: float = CACHE["tol_disp"]

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
