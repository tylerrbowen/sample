from abc import ABCMeta, abstractmethod
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster


class Era(Temporal, TemporalAdjuster):
    """
    An era of the time-line.
    Most calendar systems have a single epoch dividing the time-line into two eras.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_value(self):
        """
        Gets the numeric value associated with the era as defined by the chronology.
        @return the numeric era value
        """
        pass

    @abstractmethod
    def get_chronology(self):
        """
        Gets the chronology of this era.
        @return the chronology, not null
        """
        pass

    @abstractmethod
    def date(self, year_of_era, month, day):
        """
        Obtains a date in this era given the year-of-era, month, and day.
        @param yearOfEra  the calendar system year-of-era
        @param month  the calendar system month-of-year
        @param day  the calendar system day-of-month
        @return a local date based on this era and the specified year-of-era, month and day
        """
        pass

    @abstractmethod
    def date_year_day(self, year_of_era, day_of_year):
        """
        Obtains a date in this era given year-of-era and day-of-year fields.
        @param yearOfEra  the calendar system year-of-era
        @param dayOfYear  the calendar system day-of-year
        @return a local date based on this era and the specified year-of-era and day-of-year
        """
        pass

    @abstractmethod
    def get_display_name(self, style, locale):
        """
        Gets the textual representation of this era.
        @param style  the style of the text required, not null
        @param locale  the locale to use, not null
        @return the text value of the era, not null
        """
        pass
