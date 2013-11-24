from abc import ABCMeta, abstractmethod

class TemporalAdjuster(object):
    """
    Strategy for adjusting a temporal object.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def adjust_into(self, temporal):
        """
        Adjusts the specified temporal object.
        This adjusts the specified temporal object using the logic
        encapsulated in the implementing class.
        @param temporal  the temporal object to adjust, not null
        @return an object of the same observable type with the adjustment made, not null

        """
        raise NotImplementedError()