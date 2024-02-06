from typing import List
from typing import Union
from typing import Sequence
from typing_extensions import Literal
from typing_extensions import Annotated
from nptyping import NDArray
from nptyping import Float64

FloatNx3 = Union[
    Sequence[Annotated[List[float], 3]],
    NDArray[Literal["*, 3"], Float64],
]
"""A sequence of lists with each list containing three floats."""

FloatNx1 = Union[
    Sequence[Annotated[List[float], 1]],
    NDArray[Literal["*, 1"], Float64],
]
"""A sequence of lists with each list containing one float."""
