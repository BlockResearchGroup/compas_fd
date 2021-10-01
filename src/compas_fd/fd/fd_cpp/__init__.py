"""
******************
compas_fd.fd.fd_cpp
******************

.. currentmodule:: compas_fd.fd.fd_cpp


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fd_cpp

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .fd_cpp import fd_cpp

__all__ = []

if not compas.IPY:
    __all__ += ['fd_cpp']
