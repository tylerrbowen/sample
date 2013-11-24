from abc import ABCMeta, abstractmethod
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from ids.comparable import Comparable


class ChronoLocalDateTimeComparator:
    def compare(self, datetime1, datetime2):
        comp = datetime1.to_epoch_day().__cmp__(datetime2.to_epoch_day())
        if comp == 0:
            comp = datetime1.to_local_time().to_nano_of_day().__cmp__(datetime2.to_local_time().to_nano_of_day())
            return comp
        return comp


class ChronoLocalDateTime(Temporal, TemporalAdjuster, Comparable):
    """
    A date without time-of-day or time-zone in an arbitrary chronology, intended
    for advanced globalization use cases.
    <b>Most applications should declare method signatures, fields and variables
    as {@link LocalDate}, not this interface.</b>
    """
    __metaclass__ = ABCMeta

    DATE_COMPARATOR = ChronoLocalDateTimeComparator()

    @abstractmethod
    def to_local_date(self):
        """
        Gets the local date part of this date-time.
        """
        pass

    @abstractmethod
    def to_local_time(self):
        """
        Gets the local time part of this date-time.
        """
        pass


    @abstractmethod
    def at_zone(self, zone):
        """
        Combines this time with a time-zone to create a {@code ChronoZonedDateTime}.
        @param zone  the time-zone to use, not null
        @return the zoned date-time formed from this date-time, not null
        """
        pass

    @abstractmethod
    def to_instant(self, offset):
        """
        Converts this date-time to an {@code Instant}.
        """
        pass

    @abstractmethod
    def to_epoch_second(self, offset):
        """
        Converts this date-time to the number of seconds from the epoch
        """
        pass

    @abstractmethod
    def with_adjuster(self, adjuster):
        pass

    @abstractmethod
    def with_field(self, field, new_value):
        pass

    @abstractmethod
    def plus(self, amount_to_add=None, unit=None):
        pass

    @abstractmethod
    def plus_temporal(self, temporal_amount):
        pass

    @abstractmethod
    def minus(self, amount=None, unit=None):
        pass

    @abstractmethod
    def minus_temporal(self, temporal_amount):
        pass

    @abstractmethod
    def period_until_date(self, end_date):
        """
        Calculates the period between this date and another date as a {@code Period}.
        @param endDate  the end date, exclusive, which may be in any chronology, not null
        @return the period between this date and the end date, not null

        """
        pass

    @abstractmethod
    def at_time(self, local_time):
        """
        Combines this date with a time to create a {@code ChronoLocalDateTime}.
        """
        pass

    @abstractmethod
    def to_epoch_day(self):
        """
        Converts this date to the Epoch Day.
        @return the Epoch Day equivalent to this date
        """
        pass

    @abstractmethod
    def __cmp__(self, other):
        """
        Compares this date to another date, including the chronology.
        @param other  the other date to compare to, not null
        @return the comparator value, negative if less, positive if greater
        """
        pass

    @abstractmethod
    def is_after(self, other):
        """
        Checks if this date is after the specified date ignoring the chronology.
        """
        pass

    @abstractmethod
    def is_before(self, other):
        """
        Checks if this date is before the specified date ignoring the chronology.
        """
        pass

    @abstractmethod
    def is_equal(self, other):
        """
        Checks if this date is equal to the specified date ignoring the chronology.
        """
        pass

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError







