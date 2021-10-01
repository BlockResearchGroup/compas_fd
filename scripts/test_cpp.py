import compas
from compas.datastructures import mesh_subdivide
from compas_fd.datastructures import CableMesh
from compas_fd.fd import fd_cpp, fd_numpy
from compas_view2.app import App
from compas_view2.objects import Object, MeshObject
from timeit import timeit

Object.register(CableMesh, MeshObject)


# =================================================
# input mesh
# =================================================

mesh = CableMesh.from_obj(compas.get('faces.obj'))

mesh.vertices_attribute('is_anchor', True, mesh.vertices_where({'vertex_degree': 2}))
dva = {'rx': .0, 'ry': .0, 'rz': .0,
       'px': .0, 'py': .0, 'pz': -.0,
       'is_anchor': False}

mesh = mesh_subdivide(mesh, scheme='quad', k=1)
mesh.update_default_vertex_attributes(dva)


# =================================================
# pre-process mesh data
# =================================================

vertices = [mesh.vertex_coordinates(v) for v in mesh.vertices()]
fixed = list(mesh.vertices_where({'is_anchor': True}))
edges = list(mesh.edges())
force_densities = mesh.edges_attribute('q')
loads = mesh.vertices_attributes(['px', 'py', 'pz'])


# =================================================
# solvers
# =================================================

result_eigen = fd_cpp(vertices=vertices, fixed=fixed, edges=edges,
                      force_densities=force_densities, loads=loads)

result_np = fd_numpy(vertices=vertices, fixed=fixed, edges=edges,
                     forcedensities=force_densities, loads=loads)

forces_comparison = ((abs(l1 - l2) < 1E-14) for l1, l2
                     in zip(result_eigen.forces, result_np.forces))
print("Check if forces are equal between solvers: ", all(forces_comparison))


for vertex, coo in zip(mesh.vertices(), result_eigen.vertices):
    mesh.vertex_attributes(vertex, 'xyz', coo)


# =================================================
# benchmarks
# =================================================

def fn_cpp():
    fd_cpp(vertices=vertices, fixed=fixed, edges=edges,
           force_densities=force_densities, loads=loads)


def fn_numpy():
    fd_numpy(vertices=vertices, fixed=fixed, edges=edges,
             forcedensities=force_densities, loads=loads)


nr = 30
print(f"Solver time in cpp:   {round(1000 * timeit(fn_cpp, number=nr) / nr, 2)} ms")
print(f"Solver time in numpy: {round(1000 * timeit(fn_numpy, number=nr) / nr, 2)} ms")


# =================================================
# viz
# =================================================

viewer = App()
viewer.add(mesh)
viewer.run()
