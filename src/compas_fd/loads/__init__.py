"""
******************
compas_fd.loads
******************

.. currentmodule:: compas_fd.loads


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    LoadCalculator

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .load_calculator import LoadCalculator

__all__ = []

if not compas.IPY:
    __all__ += ['LoadCalculator']
