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

    SelfweightCalculator

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .selfweight import SelfweightCalculator

__all__ = []

if not compas.IPY:
    __all__ += ['SelfweightCalculator']
