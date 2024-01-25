from typing import List
from typing import NamedTuple
from typing_extensions import Literal
from nptyping import NDArray
from nptyping import Float64


class Result(NamedTuple):
    vertices: NDArray[Literal["*, 3"], Float64]
    residuals: NDArray[Literal["*, 3"], Float64]
    forces: List[float]
    lenghts: List[float]
