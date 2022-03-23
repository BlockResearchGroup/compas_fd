from __future__ import annotations

from typing import Sequence
from typing_extensions import Annotated

from compas.datastructures import Mesh


Vec = Annotated[Sequence[float], 3]


class Goals:
    """Represents collection of geometric and stress goals for mesh elements.

    Parameters
    ----------
    mesh : :class:`Mesh`
        Instance of Mesh datastructure.
    stress : sequence of sequence of float
        Goal 2nd Piola-Kirchhoff (σx, σy, τxy) stress field per face.
    forces : sequence of float
        Goal force per edge (default is None).
    force_densities : sequence of float
        Goal force density per edge, overwrites force goals.
    stress_ref : sequence of float
        Normal of reference plane for non-isotropic stress field orientation
        (Default is None).
    """

    def __init__(self, mesh: Mesh, stress: Sequence[Vec], forces: Sequence[float],
                 force_densities: Sequence[float], stress_ref: Vec = None):
        self.f_count = mesh.number_of_faces()
        self.stress = self._process_goal(stress, default=(1.0, 1.0, .0))
        self.force_densities = self._process_goal(force_densities)
        self.forces = self._process_goal(forces)
        self.stress_ref = stress_ref

    def _process_goal(self, goal, default=.0):
        """Construct goals as per input or to predefined defaults."""
        return goal or [default for _ in range(self.f_count)]