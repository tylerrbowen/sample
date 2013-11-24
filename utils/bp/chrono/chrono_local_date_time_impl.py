
from chrono_local_date import ChronoLocalDate
from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from utils.bp.date_time_exception import DateTimeException
from chrono_local_date_time import ChronoLocalDateTime
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from utils.bp.temporal.chrono_field import ChronoField, ChronoFieldItem
from utils.bp.local_time import LocalTime


class ChronoLocalDateTimeImpl(DefaultInterfaceTemporalAccessor, ChronoLocalDateTime, Temporal, TemporalAdjuster):

    HOURS_PER_DAY = 24
    MINUTES_PER_HOUR = 60
    MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
    SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY
    MILLIS_PER_DAY = SECONDS_PER_DAY * 1000L
    MICROS_PER_DAY = SECONDS_PER_DAY * 1000000L
    NANOS_PER_SECOND = 1000000000L
    NANOS_PER_MINUTE = NANOS_PER_SECOND * SECONDS_PER_MINUTE
    NANOS_PER_HOUR = NANOS_PER_MINUTE * MINUTES_PER_HOUR
    NANOS_PER_DAY = NANOS_PER_HOUR * HOURS_PER_DAY

    def __init__(self,
                 date,
                 time):
        self._date = date
        self._time = time

    @classmethod
    def of(cls, date, time):
        return ChronoLocalDateTimeImpl(date, time)

    def with_date_time(self, new_date, new_time):
        """
        Returns a copy of this date-time with the new date and time, checking
        to see if a new object is in fact required.
        @param newDate  the date of the new date-time, not null
        @param newTime  the time of the new date-time, not null
        @return the date-time, not null
        """
        if self._date == new_date and self._time == new_time:
            return self
        cd = self._date.get_chronology().ensure_chrono_local_date(new_date)
        return ChronoLocalDateTimeImpl(cd, new_time)

    def to_local_date(self):
        return self._date

    def to_local_time(self):
        return self._time

    def is_supported(self, field):
        if isinstance(field, ChronoFieldItem):
            f = field
            return f.is_date_field() or f.is_time_field()
        return field is not None and field.is_supported_by(self)

    def range(self, field):
        if isinstance(field, ChronoFieldItem):
            f = field
            return self._time.range(field) if f.is_time_field() else self._date.range(field)
        return field.range_refined_by(self)

    def get(self, field):
        if isinstance(field, ChronoFieldItem):
            f = field
            return self._time.get(field) if f.is_time_field() else self._date.get(field)
        return self.range(field).check_valid_int_value(self.get_long(field), field)

    def get_long(self, field):
        if isinstance(field, ChronoFieldItem):
            f = field
            return self._time.get_long(field) if f.is_time_field() else self._date.get_long(field)
        return field.get_from(self)

    def with_adjuster(self, adjuster):
        if isinstance(adjuster, ChronoLocalDate):
            return self.with_date_time(adjuster, self._time)
        elif isinstance(adjuster, LocalTime):
            return self.with_date_time(self._date, adjuster)
        elif isinstance(adjuster, ChronoLocalDateTimeImpl):
            return self._date.get_chronology().ensure_chrono_local_date_time(adjuster)
        return self._date.get_chronology().ensure_chrono_local_date_time(adjuster.adjust_into(self))

    def with_field(self, field, new_value):
        if isinstance(field, ChronoFieldItem):
            f = field
            if f.is_time_field():
                return self.with_date_time(self._date, self._time.with_field(field, new_value))
            else:
                return self.with_date_time(self._date.with_field(field, new_value), self._time)
        return self._date.get_chronology().ensure_chrono_local_date_time(field.adjust_into(self, new_value))

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            f = unit
            if f == ChronoUnit.NANOS:
                return self.plus_nanos(amount_to_add)
            elif f == ChronoUnit.MICROS:
                return self.plus_days(amount_to_add / self.MICROS_PER_DAY).plus_nanos((amount_to_add % self.MICROS_PER_DAY) * 1000)
            elif f == ChronoUnit.MILLIS:
                return self.plus_days(amount_to_add / self.MILLIS_PER_DAY).plus_nanos((amount_to_add % self.MILLIS_PER_DAY) * 1000000)
            elif f == ChronoUnit.SECONDS:
                return self.plus_seconds(amount_to_add)
            elif f == ChronoUnit.MINUTES:
                return self.plus_minutes(amount_to_add)
            elif f == ChronoUnit.HOURS:
                return self.plus_hours(amount_to_add)
            elif f == ChronoUnit.HALF_DAYS:
                return self.plus_days(amount_to_add / 256).plus_hours((amount_to_add % 256) * 12)
        return self._date.get_chronology().ensure_chrono_local_date_time(unit.add_to(self, amount_to_add))

    def plus_days(self, days):
        return self.with_date_time(self._date.plus(days, ChronoUnit.DAYS), self._time)

    def plus_hours(self, hours):
        return self.plus_with_overflow(self._date, hours, 0, 0, 0)

    def plus_minutes(self, minutes):
        return self.plus_with_overflow(self._date, 0, minutes, 0, 0)

    def plus_seconds(self, seconds):
        return self.plus_with_overflow(self._date, 0, 0, seconds, 0)

    def plus_nanos(self, nanos):
        return self.plus_with_overflow(self._date, 0, 0, 0, nanos)

    def plus_with_overflow(self, new_date, hours, minutes, seconds, nanos):
        if (hours | minutes | seconds | nanos) == 0:
            return self.with_date_time(new_date, self._time)
        tot_days = nanos / self.NANOS_PER_DAY + \
            seconds / self.SECONDS_PER_DAY + \
            minutes / self.MINUTES_PER_DAY + \
            hours / self.HOURS_PER_DAY
        tot_nanos = nanos % self.NANOS_PER_DAY + \
                    (seconds % self.SECONDS_PER_DAY) * self.NANOS_PER_SECOND + \
                    (minutes % self.MINUTES_PER_DAY) * self.NANOS_PER_MINUTE + \
                    (hours % self.HOURS_PER_DAY) * self.NANOS_PER_HOUR
        cur_no_d = self._time.to_nano_of_day()
        tot_nanos += cur_no_d
        tot_days += tot_nanos // self.NANOS_PER_DAY
        new_no_d = tot_nanos % self.NANOS_PER_DAY
        new_time = self._time if new_no_d == cur_no_d else LocalTime.of_nano_of_day(new_no_d)
        return self.with_date_time(new_date.plus(tot_days, ChronoUnit.DAYS), new_time)

    def at_zone(self, zone):
        return ChronoZoneDateTimeImpl.of_best(self, zone, None)

    def period_until(self, end_temporal, unit):
        if not isinstance(end_temporal, ChronoLocalDateTime):
            raise DateTimeException('Unable to calculate period between objects of two different types')
        end = end_temporal
        if not self.to_local_date().get_chronology().__eq__(end.to_local_date().get_chronology()):
            raise DateTimeException('Unable to calculate period between two different chronologies')
        if isinstance(unit, ChronoUnitItem):
            f = unit
            if f.is_time_unit():
                amount = end.get_long(ChronoField.EPOCH_DAY) - self._date.get_long(ChronoField.EPOCH_DAY)
                if f == ChronoUnit.NANOS:
                    amount = amount * self.NANOS_PER_DAY
                elif f == ChronoUnit.MICROS:
                    amount = amount * self.MICROS_PER_DAY
                elif f == ChronoUnit.MILLIS:
                    amount = amount * self.MILLIS_PER_DAY
                elif f == ChronoUnit.SECONDS:
                    amount = amount * self.SECONDS_PER_DAY
                elif f == ChronoUnit.MINUTES:
                    amount = amount * self.MINUTES_PER_DAY
                elif f == ChronoUnit.HOURS:
                    amount = amount * self.HOURS_PER_DAY
                elif f == ChronoUnit.HALF_DAYS:
                    amount = amount * 2
                return amount + self._time.period_unit(end.to_local_time(), unit)
            end_date = end.to_local_date()
            if end.to_local_time().is_before(self._time):
                end_date = end_date.minus(1, ChronoUnit.DAYS)
            return self._date.period_until(end_date, unit)
        return unit.between(self, end_temporal)






