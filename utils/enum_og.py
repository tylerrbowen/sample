__author__ = 'AH0137307'
from enum import Enum
from collections import OrderedDict


class EnumOG(Enum):
    def __init__(self):
        self.__dict__ = OrderedDict

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def ordinal(self, value):
        return self.__dict__.values().index(value)