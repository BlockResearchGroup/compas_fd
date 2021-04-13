from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas_fofin.rhino import CablenetHelper

find_object = sc.doc.Objects.Find


__commandname__ = 'FOFIN_splitstrip'


def splitstrip(self, uv):
    faces = []

    a, b = uv
    while True:
        fkey = self.halfedge[a][b]
        if fkey is None:
            break
        vertices = self.face_vertices(fkey)
        if len(vertices) != 4:
            break
        i = vertices.index(a)
        c = vertices[i - 2]
        d = vertices[i - 1]
        faces.append([a, b, c, d])

        del self.face[fkey]
        del self.halfedge[a][b]
        del self.halfedge[b][c]
        del self.halfedge[c][d]
        del self.halfedge[d][a]

        a, b = d, c

    faces[:] = faces[::-1]

    d, c = uv
    while True:
        fkey = self.halfedge[c][d]
        if fkey is None:
            break
        vertices = self.face_vertices(fkey)
        if len(vertices) != 4:
            break
        i = vertices.index(c)
        a = vertices[i - 2]
        b = vertices[i - 1]
        faces.append([a, b, c, d])

        del self.face[fkey]
        del self.halfedge[a][b]
        del self.halfedge[b][c]
        del self.halfedge[c][d]
        del self.halfedge[d][a]

        c, d = b, a

    a, b, c, d = faces[0]
    del self.halfedge[d][c]

    a, b, c, d = faces[-1]
    del self.halfedge[b][a]

    faces[:] = faces[::-1]

    # split the first edge
    # of the first face
    a, b, c, d = faces[0]
    x, y, z = self.edge_midpoint(a, b)
    ab = self.add_vertex(x=x, y=y, z=z)

    for a, b, c, d in faces:
        # for every face
        # split the opposite edge
        x, y, z = self.edge_midpoint(c, d)
        cd = self.add_vertex(x=x, y=y, z=z)

        # add the two new faces
        self.add_face([ab, b, c, cd])
        self.add_face([cd, d, a, ab])

        # update the edge data
        # of the split faces
        if (a, b) in self.edgedata:
            self.edgedata[a, ab] = self.edgedata[a, b]
            self.edgedata[ab, b] = self.edgedata[a, b]
        else:
            self.edgedata[a, ab] = self.edgedata[b, a]
            self.edgedata[ab, b] = self.edgedata[b, a]

        if (c, d) in self.edgedata:
            self.edgedata[c, cd] = self.edgedata[c, d]
            self.edgedata[cd, d] = self.edgedata[c, d]
        else:
            self.edgedata[c, cd] = self.edgedata[d, c]
            self.edgedata[cd, d] = self.edgedata[d, c]

        ab = cd


def RunCommand(is_interactive):
    if "FOFIN" not in sc.sticky:
        print("Initialise the plugin first!")
        return

    FOFIN = sc.sticky['FOFIN']
    if not FOFIN['cablenet']:
        return

    key = CablenetHelper.select_edge(FOFIN['cablenet'])
    if key is None:
        return

    splitstrip(FOFIN['cablenet'], key)

    FOFIN['cablenet'].draw(layer=FOFIN['settings']['layer'], clear_layer=True, settings=FOFIN['settings'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
