from typing import Any
from typing import List
from typing import Tuple
from typing import NamedTuple
from typing import Union
from nptyping import NDArray

import numpy as np


class Result(NamedTuple):
    vertices: NDArray[(Any, 3), np.float64]
    residuals: NDArray[(Any, 3), np.float64]
    forces: List[float]
    lengths: List[float]
    stresses: Union[Tuple, None] = None
