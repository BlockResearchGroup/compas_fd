"""
******************
compas_fd.fd
******************

.. currentmodule:: compas_fd.fd


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fd_numpy
    mesh_fd_numpy
    fd_cpp

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .fd_numpy import fd_numpy
    from .mesh_fd_numpy import mesh_fd_numpy
    from .fd_cpp import fd_cpp

__all__ = []

if not compas.IPY:
    __all__ += [
        'fd_numpy',
        'mesh_fd_numpy',
        'fd_cpp'
    ]
