from compas.geometry import Point, Line, Vector
from compas.geometry import Frame
import compas_rhino


__all__ = [
    'mesh_update',
    'mesh_update_xyz',
    'mesh_update_stresses',
    'mesh_update_forces'
]


def mesh_update(mesh, xyz, residuals, stresses, forces,
                res_name='r', stress_name='s', force_name='f'):
    """Update mesh with new coordinates, stresses, forces."""
    mesh_update_xyz(mesh, xyz)
    mesh_update_residuals(mesh, residuals, res_name)
    mesh_update_stresses(mesh, stresses, stress_name)
    mesh_update_forces(mesh, forces, force_name)


def mesh_update_xyz(mesh, xyz):
    """Update mesh with new vertex coordinates."""
    for vertex, coo in zip(mesh.vertices(), xyz):
        mesh.vertex_attributes(vertex, 'xyz', coo)


def mesh_update_residuals(mesh, residuals, name='r'):
    """Update mesh with new vertex coordinates."""
    for vertex, res in zip(mesh.vertices(), residuals):
        mesh.vertex_attribute(vertex, name, res)


def mesh_update_stresses(mesh, stress_data, name='s'):
    """Update mesh with face stresses."""
    stresses = stress_data.amplitudes
    vecs = stress_data.vectors
    if stresses is None:
        return
    for face, stress in zip(mesh.faces(), stresses):
        mesh.face_attribute(face, name, stress)
    if vecs is None:
        return
    for face, vec in zip(mesh.faces(), vecs):
        mesh.face_attribute(face, name + '_vecs', vec)


def mesh_update_forces(mesh, forces, name='f'):
    """Update mesh with new edge forces."""
    if forces is None:
        return
    for edge, force in zip(mesh.edges(), forces):
        mesh.edge_attribute(edge, name, force)


def draw_stresses(mesh, layer, scale=1.0, stress_name='s'):
    """Draw principal stresses as lines inside Rhino3D."""
    lines = []
    colors = (((255, 0, 0), (100, 0, 0)),
              ((0, 100, 255), (0, 0, 100)))
    for face in mesh.faces():
        center = Point(*mesh.face_center(face))
        stress, vecs = mesh.face_attributes(face,
                       [stress_name, stress_name + '_vecs'])
        if not vecs:
            return

        for i, (s, v) in enumerate(zip(stress, vecs)):
            vec = Vector(*v) * (scale * s / 2)
            p1 = (center - vec)
            p2 = (center + vec)
            lines.append({
                'start': [p1.x, p1.y, p1.z],
                'end': [p2.x, p2.y, p2.z],
                'color': colors[s >= 0][i],
                'name': "s {}".format(round(s, 5))})
    compas_rhino.draw_lines(lines, layer=layer + '::stress')


# ==============================================================================
# Main
# ==============================================================================
if __name__ == '__main__':
    pass
