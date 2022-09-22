from compas_cloud import Proxy
from compas.geometry import Point
from compas_fd.datastructures import CableMesh

from compas_fd.fd.mesh_fd_constrained_cache import mesh_fd_constrained_cache_create
from compas_fd.fd.mesh_fd_constrained_cache import mesh_fd_constrained_cache_call
from compas_fd.fd.mesh_fd_constrained_cache import mesh_fd_constrained_cache_delete

p = Proxy()
p.restart()

cablemesh = CableMesh.from_meshgrid(10, 10, 10, 10)
cablemesh.vertices_attribute(
    "is_anchor", True, keys=cablemesh.vertices_where(vertex_degree=2)
)

fd_create = p.function("compas_fd.fd.mesh_fd_constrained_cache_create")
fd_call = p.function("compas_fd.fd.mesh_fd_constrained_cache_call")
fd_delete = p.function("compas_fd.fd.mesh_fd_constrained_cache_delete")

# fd_create = mesh_fd_constrained_cache_create
# fd_call = mesh_fd_constrained_cache_call
# fd_delete = mesh_fd_constrained_cache_delete

fd_create(cablemesh, list(cablemesh.edges_where(_is_edge=True))[:10])

for i in range(10):
    scale = float(i + 1)

    xyz = fd_call(scale)
    print(xyz)

fd_delete()
