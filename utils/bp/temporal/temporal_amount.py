
from abc import ABCMeta, abstractmethod

class TemporalAmount(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_units(self):
        """
        Gets the list of units, from largest to smallest, that fully define this amount.
        @return the list of units.
        """
        pass

    @abstractmethod
    def get(self, unit):
        """
        Gets the amount associated with the specified unit.
        @param unit  the unit to get, not null
        @return the amount of the unit
        """
        pass

    @abstractmethod
    def add_to(self, temporal):
        """
        Adds to the specified temporal object.
        @param temporal  the temporal object to adjust, not null
        @return an object of the same observable type with the addition made, not null
        """
        pass

    @abstractmethod
    def subtract_from(self, temporal):
        """
        Subtracts this object from the specified temporal object.
        @param temporal  the temporal object to adjust, not null
        @return an object of the same observable type with the addition made, not null
        """
        pass


