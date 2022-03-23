"""
******************
compas_fd.nfd
******************

.. currentmodule:: compas_fd.nfd


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    nfd_ur_numpy
    nfd_numpy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .solvers import nfd_ur_numpy, nfd_numpy

__all__ = []

if not compas.IPY:
    __all__ += [
        'nfd_ur_numpy',
        'nfd_numpy'
    ]
