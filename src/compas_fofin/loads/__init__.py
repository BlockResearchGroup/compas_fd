"""
******************
compas_fofin.loads
******************

.. currentmodule:: compas_fofin.loads


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
    from .selfweight import * # noqa F401

__all__ = [name for name in dir() if not name.startswith('_')]
