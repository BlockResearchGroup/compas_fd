import compas
from compas_fd.datastructures import CableMesh

# from compas_fd.solvers import mesh_fd_numpy
from compas_view2.app import App
from compas_view2.objects import Object, MeshObject

# from compas_cloud import Proxy

Object.register(CableMesh, MeshObject)

# proxy = Proxy()
# mesh_fd = proxy.function('compas_fd.solvers.mesh_fd_numpy')

mesh = CableMesh.from_obj(compas.get("faces.obj"))

mesh.vertices_attribute(
    "is_anchor", True, keys=list(mesh.vertices_where({"vertex_degree": 2}))
)
mesh.vertices_attribute("t", 0.0)

# mesh = mesh_fd(mesh)

mesh.fd_numpy()

viewer = App()
viewer.add(mesh)
viewer.run()
