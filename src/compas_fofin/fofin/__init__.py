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

    update_xyz_numpy
    update_xyz_proxy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

if not compas.IPY:
    from .equilibrium_numpy import *


def update_xyz_proxy(data, *args, **kwargs):
    from compas_fofin.datastructures import Cablenet
    net = Cablenet.from_data(data)
    update_xyz_numpy(net, *args, **kwargs)  # noqa F405
    return net.to_data()


__all__ = [name for name in dir() if not name.startswith('_')]
