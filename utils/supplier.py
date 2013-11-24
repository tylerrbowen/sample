"""
Provide new ids for incoming objects
Factories:
Supplier
UniqueIdSupplier
ObjectIdSupplier

"""
from abc import ABCMeta, abstractmethod


class Supplier(object):
    ___metaclass__ = ABCMeta

    @abstractmethod
    def get(self):
        pass


