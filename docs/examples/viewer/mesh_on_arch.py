"""View a mesh with sliding supports along a NURBS arch."""

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Vector
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_fd.constraints import Constraint
from compas_fd.solvers import fd_constrained_numpy

# ==============================================================================
# Parameters
# ==============================================================================

size = 10.0
subdivisions = 10
boundary_force_density = 10.0
interior_force_density = 1.0
arch_control_height = 5.0

# ==============================================================================
# Mesh and supports
# ==============================================================================

midspan = size / 2
mesh = Mesh.from_meshgrid(dx=size, nx=subdivisions)
fixed = list(mesh.vertices_where(vertex_degree=2))
q = [boundary_force_density if mesh.is_edge_on_boundary(edge) else interior_force_density for edge in mesh.edges()]

arch = NurbsCurve.from_points(
    [Point(midspan, 0, 0), Point(midspan, midspan, arch_control_height), Point(midspan, size, 0)],
    degree=2,
)
sliding = list(mesh.vertices_where(x=midspan))
supports = fixed + sliding
constraints: list[Constraint[NurbsCurve] | None] = [None] * mesh.number_of_vertices()
for vertex in sliding:
    constraints[vertex] = Constraint(arch)

# ==============================================================================
# Solve
# ==============================================================================

vertices = [mesh.vertex_coordinates(vertex) for vertex in mesh.vertices()]
edges = list(mesh.edges())
result = fd_constrained_numpy(
    vertices=vertices,
    fixed=supports,
    edges=edges,
    forcedensities=q,
    constraints=constraints,
)
for vertex, xyz in zip(mesh.vertices(), result.vertices, strict=True):
    mesh.vertex_attributes(vertex, "xyz", list(xyz))

residuals = result.residuals
assert residuals is not None

# ==============================================================================
# Viewer
# ==============================================================================

config = Config()
config.window.title = "Force density | Arch-supported mesh"
config.camera.target = [midspan, midspan, 1]
config.camera.position = [-6, -9, 17]
viewer = Viewer(config=config)
viewer.scene.add(
    mesh,
    name="Equilibrium mesh",
    show_points=False,
    show_lines=True,
    linecolor=Color(0.2, 0.26, 0.34),
    hide_coplanaredges=False,
)
viewer.scene.add(
    arch.to_polyline(),
    name="Support arch",
    linecolor=Color.cyan(),
    linewidth=3,
)

for vertex in supports:
    x, y, z = mesh.vertex_coordinates(vertex)
    point = Point(x, y, z)
    color = Color.blue() if vertex in sliding else Color.red()
    viewer.scene.add(
        point,
        name=f"Support {vertex}",
        pointcolor=color,
        pointsize=10,
    )

    rx, ry, rz = residuals[vertex]
    reaction = Vector(rx, ry, rz) * -0.1
    if reaction.length > 1e-6:
        viewer.scene.add(
            Line.from_point_and_vector(point, reaction),
            name=f"Reaction {vertex}",
            linecolor=Color.green(),
            linewidth=2,
        )

viewer.show()
