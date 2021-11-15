from typing import Any
from typing import List
from typing import NamedTuple
from nptyping import NDArray

import numpy as np


class Result(NamedTuple):
    vertices: NDArray[(Any, 3), np.float64]
    residuals: NDArray[(Any, 3), np.float64]
    forces: List[float]
    lenghts: List[float]
