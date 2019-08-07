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

    find_q_numpy
    find_q_proxy
    update_xyz_numpy
    update_xyz_proxy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .forcedensity_numpy import *

if not compas.IPY:
    from .equilibrium_numpy import *


def find_q_proxy(data, *args, **kwargs):
    from compas_fofin.datastructures import Shell
    shell = Shell.from_data(data)
    find_q_numpy(shell, *args, **kwargs)
    return shell.to_data()


def update_xyz_proxy(data, *args, **kwargs):
    from compas_fofin.datastructures import Shell
    shell = Shell.from_data(data)
    update_xyz_numpy(shell, *args, **kwargs)
    return shell.to_data()


__all__ = [name for name in dir() if not name.startswith('_')]
