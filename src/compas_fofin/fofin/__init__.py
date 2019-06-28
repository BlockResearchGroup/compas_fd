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

    fofin_numpy
    fofin_numpy_proxy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .fofin_numpy import *


def fofin_numpy_proxy(data):
    from compas_fofin.datastructures import Shell
    shell = Shell.from_data(data)
    fofin_numpy(shell)
    return shell.to_data()


__all__ = [name for name in dir() if not name.startswith('_')]
