from typing import Any
from typing import List
from typing import NamedTuple
from typing import Literal
from nptyping import NDArray


import numpy as np


class Result(NamedTuple):
    vertices: NDArray[Literal["N", 3], np.float64]
    residuals: NDArray[Literal["N", 3], np.float64]
    forces: List[float]
    lenghts: List[float]
