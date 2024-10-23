from typing import Annotated
from typing import Literal
from typing import Sequence
from typing import Union

import numpy as np
import numpy.typing as npt

FloatNx3 = Union[
    Sequence[Annotated[Sequence[float], 3]],
    Annotated[npt.NDArray[np.float64], Literal["*, 3"]],
]
"""An array-like object, with each item in the array containing three (3) floats."""

FloatNx1 = Union[
    Sequence[Annotated[Sequence[float], 1]],
    Annotated[npt.NDArray[np.float64], Literal["*, 1"]],
]
"""An array-like object, with each item in the array containing one (1) float."""

IntNx2 = Union[
    Sequence[Annotated[Sequence[int], 2]],
    Annotated[npt.NDArray[np.int32], Literal["*, 2"]],
]
"""An array-like object, with each item in the array containing two (2) integers."""

IntNxM = Annotated[npt.NDArray[np.int32], Literal["*, *"]]

FloatNxM = Annotated[npt.NDArray[np.float64], Literal["*, *"]]
