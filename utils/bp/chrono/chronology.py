from abc import ABCMeta, abstractmethod
from lazr.enum import Item, MetaEnum
from utils.bp.chrono.era import Era
from utils.bp.format.date_time_formatter_builder import DateTimeFormatterBuilder
from utils.bp.instant import Instant
from utils.bp.local_time import LocalTime
from utils.bp.clock import Clock
#from utils.bp.local_date_time import LocalDateTime
from utils.bp.local_date import LocalDate
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
#from utils.bp.zoned_date_time import ZonedDateTime
from utils.bp.date_time_exception import DateTimeException
from utils.bp.temporal.temporal_queries import TemporalQueries



class Chronology(object):
    __metaclass__ = ABCMeta

    CHRONOS_BY_ID = dict()
    CHRONOS_BY_TYPE = dict()

    @classmethod
    def from_temporal(cls, temporal):
        obj = temporal.query(TemporalQueries.chronology())
        return obj if obj is not None else IsoChronology.INSTANCE()

    @classmethod
    def of_locale(cls, locale):
        type_l = locale.get_unicode_locale_type('ca')
        if type_l is None or 'iso'.__eq__(type_l) or 'iso8601'.__eq__(type_l):
            return IsoChronology.INSTANCE()
        else:
            chrono = cls.CHRONOS_BY_ID.get(type_l)
            if chrono is None:
                raise DateTimeException('')
            return chrono

    @classmethod
    def of(cls, c_id):
        chrono = cls.CHRONOS_BY_ID.get(c_id)
        if chrono is not None:
            return chrono
        raise DateTimeException('unknown chronlogy')

    @classmethod
    def get_available_chronologies(cls):
        return cls.CHRONOS_BY_ID.values()

    @classmethod
    def date_time(cls, date, time):
        #return ChronoLocalDateTimeImpl.of(date, time)
        pass


    def ensure_chrono_local_date(self, temporal):
        other = temporal
        if not self.__eq__(other.get_chronology()):
            raise Exception('Chrono mismatch')
        return other

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_calendar_type(self):
        pass

    def date(self, era, year_of_era, month, day_of_month):
        return self.proleptic_date(self.proleptic_year(era, year_of_era), month, day_of_month)

    @abstractmethod
    def proleptic_date(self, proleptic_year, month, day_of_month):
        pass

    def date_year_day(self, era, year_of_era, day_of_year):
        return self.proleptic_date_year_day(self.proleptic_year(era, year_of_era), day_of_year)

    @abstractmethod
    def proleptic_date_year_day(self, proleptic_year, day_of_year):
        pass

    @abstractmethod
    def date_temporal(self, temporal):
        pass

    def date_now(self):
        return self.date_now_clock(Clock.system_default_zone())

    def date_now_zone(self, zone):
        return self.date_now_clock(Clock.system(zone))

    def date_now_clock(self, clock):
        return self.date(LocalDate.now(clock))

    def local_date_time(self, temporal):
        """
        Obtains a local date-time in this chronology from another temporal object.
        @param temporal  the temporal object to convert, not null
        @return the local date-time in this chronology, not null
        """
        date = self.date_temporal(temporal)
        try:
            return date.at_time(LocalTime.from_temporal(temporal))
        except DateTimeException, ex:
            raise DateTimeException('Unable to obtain ChronoLocalDateTime from TemporalAccessor: ' +
                                    temporal.__class__.__name__, ex)

    def zoned_date_time_temporal(self, temporal):
        try:
            #zone = ZoneId.from_temporal(temporal)
            try:
                instant = Instant.from_temporal(temporal)
                #return self.zoned_date_time(instant, zone)
            except DateTimeException, ex:
                cldt = self.local_date_time(temporal)
                cldt_impl = self.ensure_chrono_local_date(cldt)
                #return ChronoZonedDateTimeImpl.of_best(cldt_impl, zone, None)
        except DateTimeException, ex:
            raise DateTimeException('Unable to obtain ChronoLocalDateTime from TemporalAccessor: ' +
                                    temporal.__class__.__name__, ex)

    def zoned_date_time(self, instant, zone):
        """
        Obtains a zoned date-time in this chronology from an {@code Instant}.
        @param instant  the instant to create the date-time from, not null
        @param zone  the time-zone, not null

        """
        pass
        #result = ChronoZonedDateTimeImpl.of_instant(self, instant, zone)
        #return result

    @abstractmethod
    def is_leap_year(self, proleptic_year):
        """
        Checks if the specified year is a leap year.
        @param prolepticYear  the proleptic-year to check, not validated for range
        @return true if the year is a leap year
        """
        pass

    @abstractmethod
    def proleptic_year(self, era, year_of_era):
        """
        Calculates the proleptic-year given the era and year-of-era.
        @param era  the era of the correct type for the chronology, not null
        @param yearOfEra  the chronology year-of-era
        @return the proleptic-year
        """
        pass

    @abstractmethod
    def era_of(self, era_value):
        """
        Creates the chronology era object from the numeric value.
        @param eraValue  the era value
        @return the calendar system era, not null
        """
        pass

    @abstractmethod
    def eras(self):
        """
        Gets the list of eras for the chronology.
        @return the list of eras for the chronology, may be immutable, not null
        """
        pass

    @abstractmethod
    def range(self, field):
        """
        Gets the range of valid values for the specified field.
        @param field  the field to get the range for, not null
        @return the range of valid values for the field, not null
        """
        pass

    def display_name(self, styale, locale):
        """
        Gets the textual representation of this chronology.
        @param style  the style of the text required, not null
        @param locale  the locale to use, not null
        @return the text value of the chronology, not null
        """
        raise NotImplementedError()

    def __cmp__(self, other):
        """
        Compares this chronology to another chronology.
        """
        return self.get_id().__cmp__(other.get_id())

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Chronology):
            return self.__cmp__(other) == 0
        return False

    def __hash__(self):
        return self.__class__.__name__.__hash__() ^ self.get_id().__hash__()

    def __str__(self):
        return self.get_id().__str__()



class IsoChronology(Chronology):
    """
    The ISO calendar system.
    This chronology defines the rules of the ISO calendar system.
    This calendar system is based on the ISO-8601 standard, which is the
    <i>de facto</i> world calendar.
    The fields are defined as follows:
    <li>era - There are two eras, 'Current Era' (CE) and 'Before Current Era' (BCE).
    <li>year-of-era - The year-of-era is the same as the proleptic-year for the current CE era.
    For the BCE era before the ISO epoch the year increases from 1 upwards as time goes backwards.
    <li>proleptic-year - The proleptic year is the same as the year-of-era for the
    current era. For the previous era, years have zero, then negative values.
    <li>month-of-year - There are 12 months in an ISO year, numbered from 1 to 12.
    <li>day-of-month - There are between 28 and 31 days in each of the ISO month, numbered from 1 to 31.
    Months 4, 6, 9 and 11 have 30 days, Months 1, 3, 5, 7, 8, 10 and 12 have 31 days.
    Month 2 has 28 days, or 29 in a leap year.
    <li>day-of-year - There are 365 days in a standard ISO year and 366 in a leap year.
    The days are numbered from 1 to 365 or 1 to 366.
    <li>leap-year - Leap years occur every 4 years, except where the year is divisble by 100 and not divisble by 400.
    <h3>Specification for implementors</h3>
    This class is immutable and thread-safe.
    """

    @classmethod
    def INSTANCE(cls):
        return IsoChronology()

    @classmethod
    def ERA_BCE(cls):
        return IsoEra.BCE

    @classmethod
    def ERA_CE(cls):
        return IsoEra.CE

    def __init__(self):
        return

    def get_id(self):
        return 'ISO'

    def get_calendar_type(self):
        return 'iso8601'

    def date(self, era, year_of_era, month, day_of_month):
        """
        Obtains an ISO local date from the era, year-of-era, month-of-year
        @param era  the ISO era, not null
        @param yearOfEra  the ISO year-of-era
        @param month  the ISO month-of-year
        @param dayOfMonth  the ISO day-of-month
        @return the ISO local date, not null
        """
        return self.proleptic_date(self.proleptic_year(era, year_of_era), month, day_of_month)


    #def proleptic_date(self, proleptic_year, month, day_of_month):
    #    """
    #    Obtains an ISO local date from the proleptic-year, month-of-year
    #    @param prolepticYear  the ISO proleptic-year
    #    @param month  the ISO month-of-year
    #    @param dayOfMonth  the ISO day-of-month
    #    @return the ISO local date, not null
    #    """
    #    return LocalDate.of(proleptic_year, month, day_of_month)
    #
    #def date_year_day(self, era, year_of_era, day_of_year):
    #    """
    #    Obtains an ISO local date from the era, year-of-era and day-of-year fields.
    #    @param era  the ISO era, not null
    #    @param yearOfEra  the ISO year-of-era
    #    @param dayOfYear  the ISO day-of-year
    #    @return the ISO local date, not null
    #    """
    #    return self.proleptic_date(self.proleptic_year(era, year_of_era), day_of_year)
    #
    #def proleptic_date_year_day(self, proleptic_year, day_of_year):
    #    """
    #    Obtains an ISO local date from the proleptic-year and day-of-year fields.
    #    @param prolepticYear  the ISO proleptic-year
    #    @param dayOfYear  the ISO day-of-year
    #    @return the ISO local date, not null
    #    """
    #    return LocalDate.of_year_day(proleptic_year, day_of_year)
    #
    #def date_temporal(self, temporal):
    #    """
    #    Obtains an ISO local date from another date-time object.
    #    @param temporal  the date-time object to convert, not null
    #    @return the ISO local date, not null
    #    """
    #    return LocalDate.from_temporal(temporal)
    #
    #def local_date_time(self, temporal):
    #    """
    #    Obtains an ISO local date-time from another date-time object.
    #    This is equivalent to {@link LocalDateTime#from(TemporalAccessor)}.
    #    @param temporal  the date-time object to convert, not null
    #    @return the ISO local date-time, not null
    #    """
    #    return LocalDateTime.from_temporal(temporal)
    #
    #def zoned_date_time_temporal(self, temporal):
    #    """
    #    Obtains an ISO zoned date-time from another date-time object.
    #    This is equivalent to {@link ZonedDateTime#from(TemporalAccessor)}.
    #    @param temporal  the date-time object to convert, not null
    #    @return the ISO zoned date-time, not null
    #    """
    #    return ZonedDateTime.from_temporal(temporal)
    #
    #def zoned_date_time(self, instant, zone):
    #    """
    #    Obtains an ISO zoned date-time from an instant.
    #    @param instant  the instant to convert, not null
    #    @param zone  the zone to use, not null
    #    @return the ISO zoned date-time, not null
    #    """
    #    return ZonedDateTime.of_instant(instant, zone)

    def date_now(self):
        """
        Obtains the current ISO local date from the system clock in the default time-zone.
        @return the current ISO local date using the system clock and default time-zone, not null
        """
        return self.date_now_clock(Clock.system_default_zone())

    def date_now_zone(self, zone):
        """
        Obtains the current ISO local date from the system clock in the specified time-zone.
        @return the current ISO local date using the system clock, not null
        """
        return self.date_now_clock(Clock.system(zone))

    def date_now_clock(self, clock):
        """
        Obtains the current ISO local date from the specified clock.
        @param clock  the clock to use, not null
        @return the current ISO local date, not null
        """
        return self.date_temporal(LocalDate.now(clock))

    def is_leap_year(self, proleptic_year):
        """
        Checks if the year is a leap year, according to the ISO proleptic
        calendar system rules.
        @param prolepticYear  the ISO proleptic year to check
        @return true if the year is leap, false otherwise
        """
        return ((proleptic_year & 3) == 0) and ((proleptic_year % 100) != 0 or (proleptic_year % 400) == 0)

    def proleptic_year(self, era, year_of_era):
        if not isinstance(era, IsoEra):
            raise DateTimeException('Era must be IsoEra')
        return year_of_era if era == IsoEra.CE else 1 - year_of_era

    def era_of(self, era_value):
        return IsoEra.of(era_value)

    def eras(self):
        return [x for x in IsoEra.__iter__()]

    def range(self, field):
        return field.range()


class IsoEraItem(Item, Era):
    def __init__(self,
                 title):
        super(IsoEraItem, self).__init__(title)

    def get_value(self):
        return self.sortkey

    def get_chronology(self):
        return IsoChronology.INSTANCE()

    def date(self, year_of_era, month, day):
        return self.get_chronology().date(self, year_of_era, month, day)

    def date_year_day(self, year_of_era, day_of_year):
        return self.get_chronology().date_year_day(self, year_of_era, day_of_year)

    def is_supported(self, field):
        if isinstance(field, ChronoFieldItem):
            return field == ChronoField.ERA
        return field is not None and field.is_supported(self)

    def range(self, field):
        if field == ChronoField.ERA:
            return field.range()
        elif isinstance(field, ChronoFieldItem):
            raise DateTimeException('Unsupported field: ' + field.get_name())
        return field.range_refined_by(self)

    def get(self, field):
        if field == ChronoField.ERA:
            return self.get_value()
        return self.range(field).check_valid_int_value(self.get_long(field), field)

    def get_long(self, field):
        if field == ChronoField.ERA:
            return self.get_value()
        elif isinstance(field, ChronoFieldItem):
            raise DateTimeException('Unsupported field: ' + field.get_name())
        return field.get_from(self)

    def adjust_into(self, temporal):
        return temporal.with_field(ChronoField.ERA, self.get_value())

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.get_chronology()
        return query.query_from(self)

    def get_display_name(self, style, locale):
        return DateTimeFormatterBuilder().append_text(ChronoField.ERA, style).to_formatter(locale).format(self)

    def minus(self, amount=None, unit=None):
        pass

    def minus_temporal(self, temporal_amount):
        pass

    def period_until(self, end_temporal, unit):
        pass

    def plus(self, amount_to_add=None, unit=None):
        pass

    def plus_temporal(self, temporal_amount):
        pass

    def with_adjuster(self, adjuster):
        pass

    def with_field(self, field, new_value):
        pass


class IsoEraFieldEnum(MetaEnum):
    item_type = IsoEraItem


class IsoEra:
    """
    An era in the ISO calendar system.
    The ISO-8601 standard does not define eras.
    A definition has therefore been created with two eras - 'Current era' (CE) for
    years from 0001-01-01 (ISO) and 'Before current era' (BCE) for years before that.
    <b>Do not use {@code ordinal()} to obtain the numeric representation of {@code IsoEra}.
    Use {@code getValue()} instead.</b>
    <h3>Specification for implementors</h3>
    This is an immutable and thread-safe enum.
    """

    __metaclass__ = IsoEraFieldEnum

    BCE = IsoEraItem('BCE')
    CE = IsoEraItem('CE')

    @classmethod
    def of(cls, era):
        """
        Obtains an instance of {@code IsoEra} from an {@code int} value.
        @code IsoEra} is an enum representing the ISO eras of BCE/CE.
        This factory allows the enum to be obtained from the {@code int} value.
        @param era  the BCE/CE value to represent, from 0 (BCE) to 1 (CE)
        @return the era singleton, not null
        """
        if era == 0:
            return IsoEra.BCE
        elif era == 1:
            return IsoEra.CE
        else:
            raise DateTimeException("Invalid era: " + era.__str__())

