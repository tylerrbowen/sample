from utils.bp.temporal.temporal_accessor import TemporalAccessor
from abc import ABCMeta, abstractmethod


class Temporal(TemporalAccessor):
    """
    Framework-level interface defining read-write access to a temporal object,
    such as a date, time, offset or some combination of these.
    This is the base interface type for date, time and offset objects that
    are complete enough to be manipulated using plus and minus.
    It is implemented by those classes that can provide and manipulate information
    as {@link TemporalField fields} or {@link TemporalQuery queries}.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def with_adjuster(self, adjuster):
        """
        Returns an adjusted object of the same type as this object with the adjustment made.
        @param adjuster  the adjuster to use, not null
        @return an object of the same type with the specified adjustment made, not null
        """
        raise NotImplementedError

    @abstractmethod
    def with_field(self, field, new_value):
        """
        Returns an object of the same type as this object with the specified field altered.
        @param field  the field to set in the result, not null
        @param newValue  the new value of the field in the result
        """
        raise NotImplementedError

    @abstractmethod
    def plus_temporal(self, temporal_amount):
        """
        Returns an object of the same type as this object with an amount added.
        @param amount  the amount to add, not null
        @return an object of the same type with the specified adjustment made, not null

        """
        raise NotImplementedError()

    @abstractmethod
    def plus(self, amount_to_add=None, unit=None):
        """
        Returns an object of the same type as this object with the specified period added.
        @param amountToAdd  the amount of the specified unit to add, may be negative
        @param unit  the unit of the period to add, not null
        """
        raise NotImplementedError()

    @abstractmethod
    def minus(self, amount=None, unit=None):
        """
        Returns an object of the same type as this object with an amount subtracted.
        @param amountToSubtract  the amount of the specified unit to subtract, may be negative
        @param unit  the unit of the period to subtract, not null
        @return an object of the same type with the specified adjustment made, not null
        """
        raise NotImplementedError()

    @abstractmethod
    def minus_temporal(self, temporal_amount):
        """
        Calculates the period between this temporal and another temporal in

        @param amount  the amount to subtract, not null
        @return an object of the same type with the specified adjustment made, not null
        """
        raise NotImplementedError()

    @abstractmethod
    def period_until(self, end_temporal, unit):
        """
        Calculates the period between this temporal and another temporal in
        @param endTemporal  the end temporal, of the same type as this object, not null
        @param unit  the unit to measure the period in, not null
        @return the amount of the period between this and the end
        """
        raise NotImplementedError()