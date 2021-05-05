"""
*********************
compas_fofin.analysis
*********************

.. currentmodule:: compas_fofin.analysis

Functions
=========

.. autofunction:: mesh_materialize_cables

.. autofunction:: unload_numpy

.. autofunction:: apply_loads_numpy

Proxies
=======

.. autofunction:: unload_proxy

.. autofunction:: apply_loads_proxy

"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

from .materialize import *

if not compas.IPY:
    from .unload_numpy import *

if not compas.IPY:
    from .load_numpy import *


def unload_proxy(data, *args, **kwargs):
    from compas_fofin.datastructures import Cablenet
    cablenet = Cablenet.from_data(data)
    unload_numpy(cablenet, *args, **kwargs)  # noqa F405
    return cablenet.to_data()


def apply_loads_proxy(data, *args, **kwargs):
    from compas_fofin.datastructures import Cablenet
    cablenet = Cablenet.from_data(data)
    apply_loads_numpy(cablenet, *args, **kwargs)  # noqa F405
    return cablenet.to_data()


__all__ = [name for name in dir() if not name.startswith('_')]
