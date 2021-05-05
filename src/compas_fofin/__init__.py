"""
********************************************************************************
compas_fofin
********************************************************************************

.. currentmodule:: compas_fofin


.. toctree::
    :maxdepth: 1

    compas_fofin.analysis
    compas_fofin.datastructures
    compas_fofin.fofin
    compas_fofin.loads
    compas_fofin.rhino

"""

from __future__ import print_function

import os
import compas


__author__ = ['tom van mele <van.mele@arch.ethz.ch>']
__copyright__ = 'Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'van.mele@arch.ethz.ch'
__version__ = '0.1.1rc0'


get = compas.get


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


__all__ = ['HOME', 'DATA', 'DOCS', 'TEMP', 'get']
