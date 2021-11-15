"""
******************
compas_fd.numdata
******************

.. currentmodule:: compas_fd.numdata


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    NumericalData
    FDNumericalData

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from .numerical_data import NumericalData

if not compas.IPY:
    from .fd_numerical_data import FDNumericalData

__all__ = ['NumericalData']

if not compas.IPY:
    __all__ += ['FDNumericalData']
