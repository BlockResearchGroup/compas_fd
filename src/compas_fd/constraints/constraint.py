from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.data import Data


class Constraint(Data):

    @property
    def DATASCHEMA(self):
        from schema import Schema
        return Schema()

    @property
    def JSONSCHEMANAME(self):
        return 'constraint'

    @property
    def data(self):
        return {}

    @data.setter
    def data(self, data):
        pass

    @classmethod
    def from_data(cls, data):
        return cls()

    __slots__ = ()

    def __init__(self, **kwargs):
        super(Constraint, self).__init__(**kwargs)
