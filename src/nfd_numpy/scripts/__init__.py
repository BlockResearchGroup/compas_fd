import sys
from pathlib import Path
top = str(Path(__file__).parents[1])
sys.path.append(top)

from .nfd import nfd_ur_numpy, nfd_numpy  # noqa
