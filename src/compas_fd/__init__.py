from __future__ import print_function

import os
import compas


__author__ = ["tom van mele <tom.v.mele@gmail.com>"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = "tom.v.mele@gmail.com"
__version__ = "0.5.2"


get = compas.get


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP", "get"]

__all_plugins__ = ["compas_fd.install"]
