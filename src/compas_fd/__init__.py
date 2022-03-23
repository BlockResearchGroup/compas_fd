"""
********************************************************************************
compas_fd
********************************************************************************

.. currentmodule:: compas_fd


.. toctree::
    :maxdepth: 1

    compas_fd.datastructures
    compas_fd.fd
    compas_fd.loads

"""

from __future__ import print_function

import os
import compas


__author__ = ['tom van mele <van.mele@arch.ethz.ch>']
__copyright__ = 'Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'van.mele@arch.ethz.ch'
__version__ = '0.3.1'


get = compas.get


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


__all__ = ['HOME', 'DATA', 'DOCS', 'TEMP', 'get']

__all_plugins__ = [
    'compas_fd.install'
]
