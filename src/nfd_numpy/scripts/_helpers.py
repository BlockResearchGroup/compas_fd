
__all__ = [
    'mesh_update',
    'mesh_update_xyz'
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
    stresses, vecs = stress_data
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
