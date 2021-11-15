"""
******************
compas_fd.solvers
******************

.. currentmodule:: compas_fd.solvers


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Solver
    FDSolver
    FDConstraintSolver

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from .solver import Solver
from .fd_solver import FDSolver
from .fd_constraint_solver import FDConstraintSolver

if not compas.IPY:
    pass

__all__ = ['Solver']

if not compas.IPY:
    __all__ += ['FDSolver',
                'FDConstraintSolver']
