"""
******************
compas_fofin.fofin
******************

.. currentmodule:: compas_fofin.fofin


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fd_xyz_numpy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .equilibrium_fd_numpy import *   # noqa: F401 F403


__all__ = [name for name in dir() if not name.startswith('_')]
