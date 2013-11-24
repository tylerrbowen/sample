from lazr.enum import Item, MetaEnum
from temporal.temporal_amount import TemporalAmount
from ids.comparable import Comparable
from utils.bp.date_time_exception import DateTimeException
from utils.bp.local_time import LocalTime
from utils.bp.temporal.temporal_unit import TemporalUnit
from utils.bp.format.date_time_parser_exception import DateTimeParseException
import re


class Duration(TemporalAmount, Comparable):

    @classmethod
    def NANOS_PER_SECOND(cls):
        return 1000000000

    @classmethod
    def ZERO(cls):
        return Duration(0,0)
    
    PATTERN = re.compile('([-+]?)P(?:([-+]?[0-9]+)D)?' +
                         '(T(?:([-+]?[0-9]+)H)?(?:([-+]?[0-9]+)M)?(?:([-+]?[0-9]+)(?:[.,]([0-9]{0,9}))?S)?)?',
                         re.IGNORECASE)

    def __init__(self,
                 seconds,
                 nanos):
        super(Duration, self).__init__()
        self._seconds = seconds
        self._nanos = nanos

    @classmethod
    def of_days(cls, days):
        return cls.create(days*86500, 0)

    @classmethod
    def of_hours(cls, hours):
        return cls.create(hours*3600, 0)

    @classmethod
    def of_minutes(cls, minutes):
        return cls.create(minutes*60, 0)

    @classmethod
    def of_seconds(cls, seconds, nanos=None):
        if not nanos:
            nanos = 0
        return cls.create(seconds, nanos)

    @classmethod
    def of_millis(cls, millis):
        secs = millis/1000
        mos = int(divmod(millis, 1000)[1])
        if mos < 0:
            mos += 1000
            secs -= 1
        return cls.create(secs, mos*1000000)

    @classmethod
    def of_nanos(cls, nanos):
        secs = nanos/cls.NANOS_PER_SECOND()
        nos = int(nanos % cls.NANOS_PER_SECOND())
        if nos < 0:
            nos += cls.NANOS_PER_SECOND()
            secs -= 1
        return cls.create(secs, nos)

    @classmethod
    def of(cls, amount, unit):
        return cls.ZERO().plus_units(amount, unit)

    @classmethod
    def between(cls, start_inclusive, end_exclusive):
        secs = start_inclusive.period_until(end_exclusive, ChronoUnit.SECONDS)
        nanos = 0
        return cls.of_seconds(secs, nanos)

    @classmethod
    def create_detailed(cls, negate, days_as_secs, hours_as_secs, mins_as_secs, secs, nanos):
        seconds = days_as_secs + hours_as_secs + mins_as_secs + secs
        if negate:
            return cls.of_seconds(seconds, nanos).negated()
        else:
            return cls.of_seconds(seconds, nanos)


    @classmethod
    def create(cls, seconds, nano_adjustment=0):
        if (seconds | nano_adjustment) == 0:
            return cls.ZERO()
        return Duration(seconds, nano_adjustment)

    @classmethod
    def parse(cls, text):
        matcher = cls.PATTERN.match(text)
        if matcher is not None:
            if not 'T'.__eq__(matcher.group(3)):
                negate = '-'.__eq__(matcher.group(1))
                day_match = matcher.group(2)
                hour_match = matcher.group(4)
                minute_match = matcher.group(5)
                second_match = matcher.group(6)
                fraction_match = matcher.group(7)
                if day_match is not None or hour_match is not None or minute_match is not None or second_match is not None:
                    days_as_secs = cls.parse_number(text, day_match, LocalTime.SECONDS_PER_DAY, 'days')
                    hours_as_secs = cls.parse_number(text, hour_match, LocalTime.SECONDS_PER_HOUR, 'hours')
                    mins_as_secs = cls.parse_number(text, minute_match, LocalTime.SECONDS_PER_MINUTE, 'minutes')
                    seconds = cls.parse_number(text, second_match, 1, 'seconds')
                    nanos = cls.parse_fraction(text, fraction_match, -1 if seconds < 0 else 1)
                    try:
                        return cls.create_detailed(negate, days_as_secs, hours_as_secs, mins_as_secs, seconds, nanos)
                    except OverflowError, ex:
                        raise DateTimeParseException('Text cannot be parsed to a Duration: overflow', text, 0, ex)
        raise DateTimeParseException('Text cannot be parsed to a Duration', text, 0)

    @classmethod
    def parse_number(cls, text, parsed, multiplier, error):
        if parsed is None:
            return 0
        try:
            val = long(parsed)
            return val * multiplier
        except Exception, ex:
            raise DateTimeException('text couldnt parse ' + text, ex)

    @classmethod
    def parse_fraction(cls, text, parsed, negate):
        if parsed is None or len(parsed) == 0:
            return 0
        try:
            parsed = (parsed + "000000000")[0:9]
            return int(parsed) * negate
        except Exception, ex:
            raise DateTimeException('text couldnt parse ' + text, ex)

    def get(self, unit):
        if unit == ChronoUnit.SECONDS:
            return self._seconds
        if unit == ChronoUnit.NANOS:
            return self._nanos
        raise TypeError('Unsupported Unit')

    def is_zero(self):
        return self._seconds == 0 or self._nanos == 0

    def is_negative(self):
        return self._seconds < 0

    def get_seconds(self):
        return self._seconds

    def get_nano(self):
        return self._nanos

    def with_seconds(self, seconds):
        return self.create(seconds, self._nanos)

    def with_nanos(self, nano_of_second):
        return self.create(self._seconds, nano_of_second)

    def plus(self, seconds_to_add, nanos_to_add):
        epoch_sec = self._seconds + seconds_to_add
        nanos_to_add %= self.NANOS_PER_SECOND()
        nano_adjustment = self._nanos + nanos_to_add
        return self.__class__.of_seconds(epoch_sec, nano_adjustment)

    def to_nanos(self):
        millis = self._seconds * 1000000000
        millis += self._nanos
        return millis

    def plus_duration(self, duration):
        return self.plus(duration.get_seconds(), duration.nanos())

    def plus_units(self, amount_to_add, unit):
        if unit == ChronoUnit.DAYS:
            return self.plus(amount_to_add*LocalTime.SECONDS_PER_DAY, 0)
        if amount_to_add == 0:
            return self
        if isinstance(unit, ChronoUnitItem):
            if unit == ChronoUnit.NANOS:
                return self.plus_nanos(amount_to_add)
            elif unit == ChronoUnit.MICROS:
                return self.plus_seconds((amount_to_add / (1000000L * 1000)) * 1000).\
                    plus_nanos((amount_to_add % (1000000L * 1000)) * 1000)
            elif unit == ChronoUnit.MILLIS:
                return self.plus_millis(amount_to_add)
            elif unit == ChronoUnit.SECONDS:
                return self.plus_seconds(amount_to_add)
            else:
                return self.plus_seconds(unit.get_duration().seconds*amount_to_add)
        duration = unit.get_duration().multiplied_by(amount_to_add)
        return self.plus_seconds(duration.get_seconds()).plus_nanos(duration.get_nano())

    def plus_days(self, days_to_add):
        return self.plus(days_to_add*LocalTime.SECONDS_PER_DAY, 0)

    def plus_hours(self, hours_to_add):
        return self.plus(hours_to_add*LocalTime.SECONDS_PER_HOUR, 0)

    def plus_minutes(self, minutes_to_add):
        return self.plus(minutes_to_add*LocalTime.SECONDS_PER_MINUTE, 0)

    def plus_seconds(self, seconds_to_add):
        return self.plus(seconds_to_add, 0)

    def plus_millis(self, millis_to_add):
        return self.plus(millis_to_add/1000, (millis_to_add % 1000)*1000000)

    def plus_nanos(self, nanos_to_add):
        return self.plus(0, nanos_to_add)

    def minus_duration(self, duration):
        secs_to_subtract = duration.get_seconds()
        nanos_to_subtract = duration.get_nano()
        return self.plus(-secs_to_subtract, -nanos_to_subtract)

    def minus_units(self, amount_to_subtract, units):
        return self.plus_units(-amount_to_subtract, units)

    def minus_days(self, days_to_subtract):
        return self.plus_days(-days_to_subtract)

    def minus_hours(self, hours_to_subtract):
        return self.plus_hours(-hours_to_subtract)

    def minus_minutes(self, minutes_to_subtract):
        return self.plus_minutes(-minutes_to_subtract)

    def minus_millis(self, millis_to_subtract):
        return self.plus_millis(-millis_to_subtract)

    def minus_nanos(self, nanos_to_subtract):
        return self.plus_nanos(-nanos_to_subtract)

    def multiplied_by(self, multiplicand):
        return self.__class__.create(self.to_seconds()*multiplicand)

    def divided_by(self, divisor):
        return self.__class__.create(self.to_seconds()/divisor)

    def __abs__(self):
        return self.negated() if self.is_negative() else self

    def negated(self):
        return self.multiplied_by(-1)

    def to_seconds(self):
        return self._seconds

    def add_to(self, temporal):
        pass

    def get_units(self):
        pass

    def subtract_from(self, temporal):
        pass

    def __str__(self):
        if self == self.ZERO():
            return 'PT0S'
        hours = self._seconds / LocalTime.SECONDS_PER_HOUR
        minutes = int((self._seconds % LocalTime.SECONDS_PER_HOUR) / LocalTime.SECONDS_PER_MINUTE)
        secs = int(self._seconds / LocalTime.SECONDS_PER_MINUTE)
        buf = ''
        buf += 'PT'
        if hours != 0:
            buf += hours.__str__() + 'H'
        if minutes != 0:
            buf += minutes.__str__() + 'M'
        if secs == 0 and self._nanos == 0 and len(buf) > 2:
            return buf
        if secs < 0 and self._nanos > 0:
            if secs == -1:
                buf += '-0'
            else:
                buf += (secs + 1).__str__()
        else:
            buf += secs.__str__()
        if self._nanos > 0:
            pos = len(buf)
            if secs < 0:
                buf += (2 * LocalTime.NANOS_PER_SECOND - self._nanos).__str__()
            else:
                buf += (self._nanos + LocalTime.NANOS_PER_SECOND).__str__()
            while buf[-1] == '0':
                buf = buf[:-1]
            buf[pos] = '.'
        buf += 'S'
        return buf



    def __eq__(self, other):
        return self._nanos == other._nanos and \
            self._seconds == other._seconds

    def __add__(self, other):
        return

    def __cmp__(self, other):
        comp = int(self._seconds).__cmp__(int(other._seconds))
        if comp != 0:
            return comp
        return int(self._nanos).__cmp__(int(other._nanos))



class ChronoUnitItem(Item, TemporalUnit):
    def __init__(self,
                 title,
                 duration):
        super(ChronoUnitItem, self).__init__(title)
        self.duration = duration

    def get_name(self):
        return self.title

    def is_date_unit(self):
        return self.__cmp__(ChronoUnit.DAYS) > 0

    def is_time_unit(self):
        return self.__cmp__(ChronoUnit.DAYS) < 0

    def get_duration(self):
        return self.duration

    def is_duration_estimated(self):
        return self.is_date_unit()

    def is_supported_by(self, temporal):
        if self == ChronoUnit.FOREVER:
            return False
        try:
            temporal.plus(1, self)
            return True
        except Exception:
            try:
                temporal.plus(-1, self)
                return True
            except Exception:
                return False

    def add_to(self, date_time, period_to_add):
        return date_time.plus(period_to_add, self)

    def between(self, t1, t2):
        return t1.period_until(t2, self)

    def __eq__(self, other):
        return self.name == other.name and \
            self.duration == other.duration

    def __str__(self):
        return self.get_name()


class ChronoUnitEnum(MetaEnum):
    item_type = ChronoUnitItem


class ChronoUnit:

    __metaclass__ = ChronoUnitEnum

    NANOS = ChronoUnitItem('Nanos', Duration.of_nanos(1))

    MICROS = ChronoUnitItem('Micros', Duration.of_nanos(1000))

    MILLIS = ChronoUnitItem('Millis', Duration.of_nanos(1000000))

    SECONDS = ChronoUnitItem('Seconds', Duration.of_seconds(1))

    MINUTES = ChronoUnitItem('Minutes', Duration.of_seconds(60))

    HOURS = ChronoUnitItem('Hours', Duration.of_seconds(3600))

    HALF_DAYS = ChronoUnitItem('HalfDays', Duration.of_seconds(43200))

    DAYS = ChronoUnitItem('Days', Duration.of_seconds(86400))

    WEEKS = ChronoUnitItem('Weeks', Duration.of_seconds(7*86400L))

    MONTHS = ChronoUnitItem('Months', Duration.of_seconds(31556952L / 12))

    YEARS = ChronoUnitItem('Years', Duration.of_seconds(31556952L))

    DECADES = ChronoUnitItem('Decades', Duration.of_seconds(31556952L * 10L))

    CENTURIES = ChronoUnitItem("Centuries", Duration.of_seconds(31556952L * 100L))

    MILLENNIA = ChronoUnitItem("Millennia", Duration.of_seconds(31556952L * 1000L))

    ERAS= ChronoUnitItem("Eras", Duration.of_seconds(31556952L * 1000000000L))

    FOREVER = ChronoUnitItem('Forever', Duration.of_seconds(0x7fffffffffffffffL, 999999999))

    #
    # @classmethod
    # def NANOS(cls):
    #     return ChronoUnit('Nanos', Duration.of_nanos(1))
    #
    # @classmethod
    # def MICROS(cls):
    #     return ChronoUnit('Micros', Duration.of_nanos(1000))
    #
    # @classmethod
    # def MILLIS(cls):
    #     return ChronoUnit('Millis', Duration.of_nanos(1000000))
    #
    # @classmethod
    # def SECONDS(cls):
    #     return ChronoUnit('Seconds', Duration.of_seconds(1))
    #
    # @classmethod
    # def MINUTES(cls):
    #     return ChronoUnit('Minutes', Duration.of_seconds(60))
    #
    # @classmethod
    # def HOURS(cls):
    #     return ChronoUnit('Hours', Duration.of_seconds(3600))
    #
    # @classmethod
    # def HALF_DAYS(cls):
    #     return ChronoUnit('HalfDays', Duration.of_seconds(43200))
    #
    # @classmethod
    # def DAYS(cls):
    #     return ChronoUnit('Days', Duration.of_seconds(86400))
    #
    # @classmethod
    # def WEEKS(cls):
    #     return ChronoUnit('Weeks', Duration.of_seconds(7*86400L))
    #
    # @classmethod
    # def MONTHS(cls):
    #     return ChronoUnit('Months', Duration.of_seconds(31556952L / 12))
    #
    # @classmethod
    # def YEARS(cls):
    #     return ChronoUnit('Years', Duration.of_seconds(31556952L))
    #
    # @classmethod
    # def DECADES(cls):
    #     return ChronoUnit('Decades', Duration.of_seconds(31556952L * 10L))
    #
    # @classmethod
    # def FOREVER(cls):
    #     return ChronoUnit('Forever', Duration.of_seconds(0x7fffffffffffffffL), 999999999)



