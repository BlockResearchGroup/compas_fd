from typing import Callable
from functools import wraps

from ..result import Result


class NumericalData:
    """Storage class for numerical arrays used by solver algorithms."""

    @classmethod
    def from_mesh(cls, mesh):
        """Construct numerical arrays from input mesh."""
        raise NotImplementedError

    def to_result(self) -> Result:
        """Parse relevant numerical data into a Result object."""
        raise NotImplementedError


def lazy_eval(getter: Callable) -> Callable:
    """Decorator for lazy evaluation on property getters.

    A private attribute name is assumed as ('_' + getter name).
    The computation in the getter function is done only if:
        - the private attribute does not exist in the instance dictionary.
        - or the private attribute is None.
    After computation by the getter function, the private attribute is stored
    in the instance attribute dictionary.
    """
    private_attr = '_' + getter.__name__

    @wraps(getter)
    def wrapper(self, *args, **kwargs):
        attr = getattr(self, private_attr, None)
        if attr is None:
            attr = getter(self, *args, **kwargs)
            self.__dict__[private_attr] = attr
        return attr
    return wrapper
