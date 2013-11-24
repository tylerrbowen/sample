import datetime as dt
from pytz import timezone
import delorean
import pytz
import re

from ids.comparable import Comparable
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.chrono_field import ChronoField, ChronoFieldItem
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.local_time import LocalTime
from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from utils.bp.date_time_exception import DateTimeException


class Instant(DefaultInterfaceTemporalAccessor, Temporal, TemporalAdjuster, Comparable):
    """
    An instantaneous point on the time-line.
    This class models a single instantaneous point on the time-line.
    This might be used to record event time-stamps in the application.
    For practicality, the instant is stored with some constraints.
    The measurable time-line is restricted to the number of seconds that can be held
    in a {@code long}. This is greater than the current estimated age of the universe.
    The instant is stored to nanosecond resolution.
    The range of an instant requires the storage of a number larger than a {@code long}.
    To achieve this, the class stores a {@code long} representing epoch-seconds and an
    {@code int} representing nanosecond-of-second, which will always be between 0 and 999,999,999.
    The epoch-seconds are measured from the standard Java epoch of {@code 1970-01-01T00:00:00Z}
    where instants after the epoch have positive values, and earlier instants have negative values.
    For both the epoch-second and nanosecond parts, a larger value is always later on the time-line
    than a smaller value.

    Long MAX VALUE: 0x7fffffffffffffffL
    Long MIN VALUE: 0x8000000000000000L
    """

    EPOCH_START = dt.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.utc)
    LOCAL_DEFAULT = 'US/Eastern'

    def __init__(self, epoch_second, nanos):
        self.seconds = long(epoch_second)
        self.nanos = int(nanos)

    @classmethod
    def of(cls, seconds, nanos):
        return Instant(seconds, nanos)

    def get_long(self, field):
        pass

    def is_supported(self, field):
        pass

    @classmethod
    def EPOCH(cls):
        return Instant(0, 0)

    @classmethod
    def MIN_SECOND(cls):
        return -31557014167219200L

    @classmethod
    def MAX_SECOND(cls):
        return 31556889864403199L

    @classmethod
    def MIN(cls):
        return cls.of(cls.MIN_SECOND(), 0)

    @classmethod
    def MAX(cls):
        return cls.of_epoch_second(cls.MAX_SECOND(), 999999999)

    @classmethod
    def NANOS_PER_SECOND(cls):
        return 1000000000

    @classmethod
    def create(cls, seconds, nano_of_second):
        if (int(seconds) | int(nano_of_second)) == 0:
            return cls.EPOCH()
        if seconds < cls.MIN_SECOND() or seconds > cls.MAX_SECOND():
            raise DateTimeException('Instant exceeds minimum or maximum instant')
        return Instant(seconds, nano_of_second)

    @classmethod
    def from_temporal(cls, temporal):
        """
        Obtains an instance of {@code Instant} from a temporal object.
        @param temporal  the temporal object to convert, not null
        @return the instant, not null
        """
        instant_secs = temporal.get_long(ChronoField.INSTANT_SECONDS)
        nano_of_second = temporal.get(ChronoField.NANO_OF_SECOND)
        return Instant.of_epoch_second(instant_secs, nano_of_second)


    @classmethod
    def now(cls):
        now = delorean.localize(dt.datetime.now(),
                                'UTC')
        diff = now - dt.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.utc)
        millis = (diff.days * 24 * 60 * 60 + diff.seconds) * 1000 + diff.microseconds / 1000
        return cls.of_epoch_milli(millis)

    @classmethod
    def now_clock(cls, clock):
        return clock.instant()

    @classmethod
    def of_epoch_second(cls, epoch_second, nano_adjustment=0):
        return cls.create(epoch_second, nano_adjustment)

    @classmethod
    def of_epoch_milli(cls, epoch_milli):
        secs = epoch_milli // 1000
        mos = epoch_milli % 1000
        return cls.create(secs, mos*1000000)

    def get_epoch_second(self):
        return self.seconds

    def get_nano(self):
        return self.nanos

    def period_until(self, end_instant, unit):
        """
        Calculates the period between this instant and another instant in
        terms of the specified unit.
        This calculates the period between two instants in terms of a single unit.
        The start and end points are {@code this} and the specified instant.
        The result will be negative if the end is before the start.
        The calculation returns a whole number, representing the number of
        complete units between the two instants.
        @param endInstant  the end date, which must be a {@code LocalDate}, not null
        @param unit  the unit to measure the period in, not null
        @return the amount of the period between this date and the end date
        """
        end = end_instant
        f = unit
        if f is ChronoUnit.NANOS:
            return self.nanos_until(end)
        elif f == ChronoUnit.MICROS:
            return self.nanos_until(end)/1000.
        elif f == ChronoUnit.MILLIS:
            return end.to_epoch_milli() - self.to_epoch_milli()
        elif f == ChronoUnit.SECONDS:
            return self.seconds_until(end)
        elif f == ChronoUnit.MINUTES:
            return self.seconds_until(end) / LocalTime.SECONDS_PER_MINUTE
        elif f == ChronoUnit.HOURS:
            return self.seconds_until(end) / LocalTime.SECONDS_PER_HOUR
        elif f == ChronoUnit.HALF_DAYS:
            return self.seconds_until(end) / (12*LocalTime.SECONDS_PER_HOUR)
        elif f == ChronoUnit.DAYS:
            return self.seconds_until(end)/ (LocalTime.SECONDS_PER_DAY)
        else:
            raise Exception

    def nanos_until(self, end):
        secs = self.seconds_until(end) * LocalTime.NANOS_PER_SECOND
        return secs + end.nanos - self.nanos

    def truncated_to(self, unit):
        if unit == ChronoUnit.NANOS:
            return self
        unit_dur = unit.get_duration()
        if unit_dur.get_seconds() > LocalTime.SECONDS_PER_DAY:
            raise DateTimeException
        dur = unit_dur.to_nanos()
        nod = (self.seconds % LocalTime.SECONDS_PER_DAY) * LocalTime.NANOS_PER_SECOND + self.nanos
        result  = (nod / dur) * dur
        return self.plus_nanos(result - nod)

    def seconds_until(self, end):
        return end.seconds - self.seconds

    def adjust_into(self, temporal):
        """
        Adjusts the specified temporal object to have this instant.
        This returns a temporal object of the same observable type as the input
        with the instant changed to be the same as this.
        @param temporal  the target object to be adjusted, not null
        @return the adjusted object, not null
        """
        return temporal.with_field(ChronoField.INSTANT_SECONDS, self.seconds).\
            with_field(ChronoField.NANO_OF_SECOND, self.nanos)

    def with_adjuster(self, adjuster):
        """
        Returns an adjusted copy of this instant.
        This returns a new {@code Instant}, based on this one, with the date adjusted.
        The adjustment takes place using the specified adjuster strategy object.
        @param adjuster the adjuster to use, not null
        @return an {@code Instant} based on {@code this} with the adjustment made, not null
        """
        return adjuster.adjust_into(self)

    def with_field(self, field, new_value):
        """
        Returns a copy of this instant with the specified field set to a new value.
        This returns a new {@code Instant}, based on this one, with the value
        for the specified field changed.
        If it is not possible to set the value, because the field is not supported or for
        some other reason, an exception is thrown.
        @param field  the field to set in the result, not null
        @param newValue  the new value of the field in the result
        @return an {@code Instant} based on {@code this} with the specified field set, not null
        @throws DateTimeException if the field cannot be set
        """
        if isinstance(field, ChronoFieldItem):
            f = field
            f.check_valid_int_value(new_value)
            if f == ChronoField.MILLI_OF_SECOND:
                nval = int(new_value * 1000000)
                return Instant.create(self.seconds, nval) if nval != self.seconds else self
            elif f == ChronoField.MICRO_OF_SECOND:
                nval = int(new_value * 1000)
                return Instant.create(self.seconds, nval) if nval != self.seconds else self
            elif f == ChronoField.NANO_OF_SECOND:
                return Instant.create(self.seconds, new_value) if new_value != self.nanos else self
            elif f == ChronoField.INSTANT_SECONDS:
                return Instant.create(new_value, self.nanos) if new_value != self.seconds else self
            else:
                raise DateTimeException('Unsupported Field: ' + field.get_name())
        return field.adjust_into(self, new_value)

    def plus_temporal(self, temporal_amount):
        """
        Returns an object of the same type as this object with an amount added.
        """
        return temporal_amount.add_to(self)

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            if unit == ChronoUnit.NANOS:
                return self.plus_nanos(amount_to_add)
            elif unit == ChronoUnit.MICROS:
                return self.plus_seconds_nanos(amount_to_add / 1000000., (amount_to_add % 1000000) * 1000)
            elif unit == ChronoUnit.MILLIS:
                return self.plus_millis(amount_to_add)
            elif unit == ChronoUnit.SECONDS:
                return self.plus_seconds(amount_to_add)
            elif unit == ChronoUnit.MINUTES:
                return self.plus_seconds(amount_to_add * LocalTime.SECONDS_PER_MINUTE)
            elif unit == ChronoUnit.HOURS:
                return self.plus_seconds(amount_to_add * LocalTime.SECONDS_PER_HOUR)
            elif unit == ChronoUnit.HALF_DAYS:
                return self.plus_seconds(amount_to_add * LocalTime.SECONDS_PER_DAY / 2)
            elif unit == ChronoUnit.DAYS:
                return self.plus_seconds(amount_to_add * LocalTime.SECONDS_PER_DAY)
            else:
                raise DateTimeException('Unsupported unit: ' + unit.get_name())
        return amount_to_add.add_to(self)

    def plus_millis(self, millis_to_add):
        """
        Returns a copy of this instant with the specified duration in milliseconds added.
        This instance is immutable and unaffected by this method call.
        @param millisToAdd  the milliseconds to add, positive or negative
        @return an {@code Instant} based on this instant with the specified milliseconds added, not null
        """
        return self.plus_seconds_nanos(millis_to_add / 1000, (millis_to_add % 1000) * 1000000)

    def plus_nanos(self, nanos_to_add):
        """
        Returns a copy of this instant with the specified duration in nanoseconds added.
        This instance is immutable and unaffected by this method call.
        @param nanosToAdd  the nanoseconds to add, positive or negative
        @return an {@code Instant} based on this instant with the specified nanoseconds added, not null
        """
        return self.plus_seconds_nanos(0, nanos_to_add)

    def plus_seconds(self, seconds_to_add):
        """
        Returns a copy of this instant with the specified duration in seconds added.
        This instance is immutable and unaffected by this method call.
        @param seoncds_to_add the seconds to add, positive or negative
        @return an {@code Instant} based on this instant with the specified nanoseconds added, not null
        """
        return self.plus_seconds_nanos(seconds_to_add, 0)


    def plus_seconds_nanos(self, seconds_to_add, nanos_to_add):
        """
        Returns a copy of this instant with the specified duration added.
        This instance is immutable and unaffected by this method call.
        @param secondsToAdd  the seconds to add, positive or negative
        @param nanosToAdd  the nanos to add, positive or negative
        @return an {@code Instant} based on this instant with the specified seconds added, not null
        """
        if (seconds_to_add | nanos_to_add) == 0:
            return self
        epoch_sec = self.seconds + seconds_to_add
        epoch_sec += nanos_to_add / self.NANOS_PER_SECOND()
        nanos_to_add %= self.NANOS_PER_SECOND()
        nano_adjustment = self.nanos + nanos_to_add
        return Instant.of_epoch_second(epoch_sec, nano_adjustment)

    def minus_temporal(self, temporal_amount):
        return temporal_amount.subtract_from(self)

    def minus(self, amount=None, unit=None):
        if amount == 0x8000000000000000L:
            return self.plus(0x7fffffffffffffffL, unit).plus(1, unit)
        else:
            return self.plus(-amount, unit)

    def minus_seconds(self, seconds_to_subtract):
        if seconds_to_subtract == 0x8000000000000000L:
            return self.plus_seconds(0x7fffffffffffffffL).plus_seconds(1)
        else:
            return self.plus_seconds(-seconds_to_subtract)

    def minus_millis(self, millis_to_subtract):
        if millis_to_subtract == 0x8000000000000000L:
            return self.plus_millis(0x7fffffffffffffffL).plus_millis(1)
        else:
            return self.plus_millis(-millis_to_subtract)

    def minus_nanos(self, nanos_to_subtract):
        if nanos_to_subtract == 0x8000000000000000L:
            return self.plus_nanos(0x7fffffffffffffffL).plus_nanos(1)
        else:
            return self.plus_nanos(-nanos_to_subtract)

    def query(self, query):
        """
        Queries this instant using the specified query.
        This queries this instant using the specified query strategy object.
        The {@code TemporalQuery} object defines the logic to be used to
        obtain the result. Read the documentation of the query to understand
        what the result of this method will be.
        The result of this method is obtained by invoking the
        {@link TemporalQuery#queryFrom(TemporalAccessor)} method on the
        specified query passing {@code this} as the argument.
        @param <R> the type of the result
        @param query  the query to invoke, not null
        @return the query result, null may be returned (defined by the query)

        """
        if query == TemporalQueries.precision():
            return ChronoUnit.NANOS

        if query == TemporalQueries.chronology() or \
                        query == TemporalQueries.zone_id() or \
                        query == TemporalQueries.zone() or \
                        query == TemporalQueries.offset():
            return None
        return query.query_from(self)

    def at_offset(self, offset):
        """
        Combines this instant with an offset to create an {@code OffsetDateTime}.
        This returns an {@code OffsetDateTime} formed from this instant at the
        specified offset from UTC/Greenwich. An exception will be thrown if the
        instant is too large to fit into an offset date-time.
        @param offset  the offset to combine with, not null
        @return the offset date-time formed from this instant and the specified offset, not null

        """
        #return OffsetDateTime.of_instant(self, offset)
        raise NotImplementedError()

    def at_zone(self, zone):
        #return ZoneDateTime.of_instant(self, zone)
        raise NotImplementedError()

    def to_epoch_milli(self):
        """
        Converts this instant to the number of milliseconds from the epoch
        of 1970-01-01T00:00:00Z.
        If this instant represents a point on the time-line too far in the future
        or past to fit in a {@code long} milliseconds, then an exception is thrown.
        @return the number of milliseconds since the epoch of 1970-01-01T00:00:00Z

        """
        millis = self.seconds * 1000
        return millis + self.nanos / 1000000

    def __cmp__(self, other):
        comp = self.seconds - other.seconds
        if comp != 0:
            return 1 if comp > 0 else -1
        return self.nanos - other.nanos

    def is_after(self, other):
        """
        Checks if this instant is before the specified instant.
        The comparison is based on the time-line position of the instants.
        @param otherInstant  the other instant to compare to, not null
        @return true if this instant is before the specified instant
        """
        return self.__cmp__(other) > 0

    def is_before(self, other):
        """
        Checks if this instant is after the specified instant.
        The comparison is based on the time-line position of the instants.
        @param otherInstant  the other instant to compare to, not null
        @return true if this instant is after the specified instant
        """
        return self.__cmp__(other) < 0

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Instant):
            return self.seconds == other.seconds
        return False

    def __hash__(self):
        return  int(self.seconds ^ (self.seconds >> 32 )) + 51 * self.nanos

    def __str__(self):
        ltime = self.to_local_datetime(self.LOCAL_DEFAULT)
        return ltime.strftime('%Y-%m-%d %H:%M:%S.%f')

    @classmethod
    def parse(cls, text):
        # iso_pattern = '(\d{4}\-\d\d\-\d\d)(([tT])?([\d:\.]*))?([zZ]|([+\-])(\d\d):?(\d\d))?$'
        # iso_re = re.compile(iso_pattern)
        time_zone_input = timezone(cls.LOCAL_DEFAULT)
        # matcher = iso_re.match(text)
        # if matcher is None:
        #     dstring =
        # else:
        #     dstring = matcher.group(1) + ' ' + matcher.group(4)
        input_datetime = time_zone_input.localize(dt.datetime.strptime(text, '%Y-%m-%d %H:%M:%S.%f'))
        utc_datetime = input_datetime.astimezone(pytz.utc)
        diff = utc_datetime - cls.EPOCH_START
        tot_secs = (diff.days * 86400 + diff.seconds)
        nano_adjustment = (diff.microseconds * 1000)
        return cls.of_epoch_second(tot_secs, nano_adjustment)

    def to_local_datetime(self, tz_name):
        local_tz = timezone(tz_name)
        seconds = self.seconds
        micros = self.nanos / 1000
        days = seconds // 86400
        seconds %= 86400
        timedelta = dt.timedelta(days, seconds, micros)
        utc_datetime = self.EPOCH_START + timedelta
        local_datetime = local_tz.normalize(utc_datetime.astimezone(local_tz))
        return local_datetime

    @classmethod
    def from_dt_datetime(cls, dt_datetime):
        time_zone_input = timezone(cls.LOCAL_DEFAULT)
        input_datetime = time_zone_input.localize(dt_datetime)
        utc_datetime = input_datetime.astimezone(pytz.utc)
        diff = utc_datetime - cls.EPOCH_START
        tot_secs = (diff.days * 86400 + diff.seconds)
        nano_adjustment = (diff.microseconds * 1000)
        return cls.of_epoch_second(tot_secs, nano_adjustment)












