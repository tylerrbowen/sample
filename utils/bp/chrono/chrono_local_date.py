from abc import ABCMeta, abstractmethod
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from ids.comparable import Comparable


class ChronoLocalDateComparator:
    def compare(self, date1, date2):
        return date1.to_epoch_day().__cmp__(date2.to_epoch_day())



class ChronoLocalDate(Temporal, TemporalAdjuster, Comparable):
    """
    A date without time-of-day or time-zone in an arbitrary chronology, intended
    for advanced globalization use cases.
    <b>Most applications should declare method signatures, fields and variables
    as {@link LocalDate}, not this interface.</b>
    """
    __metaclass__ = ABCMeta

    DATE_COMPARATOR = ChronoLocalDateComparator()

    @abstractmethod
    def get_chronology(self):
        """
        Gets the chronology of this date.
        @return the chronology, not null
        """
        pass

    @abstractmethod
    def get_era(self):
        """
        Gets the era, as defined by the chronology.
        @return the chronology specific era constant applicable at this date, not null
        """
        pass

    @abstractmethod
    def is_leap_year(self):
        """
        Checks if the year is a leap year, as defined by the calendar system.
        @return true if this date is in a leap year, false otherwise
        """
        pass

    @abstractmethod
    def length_of_month(self):
        """
        Returns the length of the month represented by this date, as defined by the calendar system.
        @return the length of the month in days
        """
        pass

    @abstractmethod
    def length_of_year(self):
        """
        Returns the length of the year represented by this date, as defined by the calendar system.
        @return the length of the year in days
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






