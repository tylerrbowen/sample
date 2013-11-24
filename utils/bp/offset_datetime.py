import datetime
from utils.bp.default.default_interface_temporal import DefaultInterfaceTemporal
from ids.comparable import Comparable
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.temporal import Temporal
from utils.bp.zoned_date_time import ZonedDateTime
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.date_time_exception import DateTimeException
from utils.bp.instant import Instant
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
from local_date_time import LocalDateTime
from local_date import LocalDate
from local_time import LocalTime
from utils.bp.clock import Clock
from utils.bp.zone_offset import ZoneOffset


class OffsetDateTime(DefaultInterfaceTemporal, Temporal, TemporalAdjuster, Comparable):

    def __init__(self,
                 local_datetime,
                 offset):
        self._datetime = local_datetime
        self._offset = offset

    @classmethod
    def now(cls, zone=None, clock=None):
        if clock is None:
            if zone is None:
                return cls.now(zone=Clock.system_default_zone())
            else:
                return cls.now(Clock.system(zone))
        now = clock.instant()
        return cls.of_instant(now, clock.get_zone())

    @classmethod
    def of_local_date(cls, date, time, offset):
        ldt = LocalDateTime.of(date, time)
        return OffsetDateTime(ldt, offset)

    @classmethod
    def of_local_datetime(cls, datetime, offset):
        return OffsetDateTime(datetime, offset)

    @classmethod
    def of(cls, year, month, day_of_month, hour, minute, second, nano_of_second, offset):
        ldt = LocalDateTime.of_components(year,
                                          month,
                                          day_of_month,
                                          hour,
                                          minute,
                                          second,
                                          nano_of_second)
        return OffsetDateTime(ldt, offset)

    @classmethod
    def of_instant(cls, instant, zone):
        rules = zone.get_rules()
        offset = rules.get_offset(instant)
        ldt = LocalDateTime.of_epoch_second(instant.get_epoch_second(), instant.get_nano(), offset)
        return OffsetDateTime(ldt, offset)

    @classmethod
    def from_temporal(cls, temporal):
        if isinstance(temporal, OffsetDateTime):
            return temporal
        offset = ZoneOffset.from_temporal(temporal)
        try:
            try:
                ldt = LocalDateTime.from_temporal(temporal)
                return OffsetDateTime(ldt, offset)
            except DateTimeException, ex:
                instant = Instant.from_temporal(temporal)
                return OffsetDateTime.of_instant(instant, offset)
        except DateTimeException, ex:
            raise DateTimeException(
                'Unable to obtain OffsetDateTime from TemporalAccessor: ' + temporal.__class__.__name__, ex)

    @classmethod
    def parse(cls, text):
        datetimedate = datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S %Z')
        ldt = LocalDateTime.parse(text)
        tz_name = datetimedate.tzname()
        offset = ZoneOffset.of(tz_name)
        return OffsetDateTime(ldt, offset)

    def with_datetime_offset(self, date_time, offset):
        return OffsetDateTime(date_time, offset)

    def is_supported(self, field):
        return isinstance(field, ChronoFieldItem) or (field is not None and field.is_supported_by(self))

    def range(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS or field == ChronoField.OFFSET_SECONDS:
                return field.range()
            return self._datetime.range(field)
        return field.range_refined_by(self)

    def get(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS:
                raise DateTimeException('too large')
            elif field == ChronoField.OFFSET_SECONDS:
                return self.get_offset().get_total_seconds()
            return self._datetime.get(field)
        return super(OffsetDateTime, self).get(field)

    def get_long(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS:
                return self.to_epoch_seconds()
            elif field == ChronoField.OFFSET_SECONDS:
                return self.get_offset().get_total_seconds()
            return self._datetime.get_long(field)
        return field.get_from(self)

    def get_offset(self):
        return self._offset

    def with_offset_same_local(self, offset):
        return self.with_datetime_offset(self._datetime, offset)

    def with_offset_same_instant(self, offset):
        difference = offset.get_total_seconds() - self._offset.get_total_seconds()
        adjusted = self._datetime.plus_seconds(difference)
        return OffsetDateTime(adjusted, offset)

    def get_year(self):
        return self._datetime.get_year()

    def get_month_value(self):
        return self._datetime.get_month_value()

    def get_month(self):
        return self._datetime.get_month()

    def get_day_of_month(self):
        return self._datetime.get_day_of_month()

    def get_day_of_year(self):
        return self._datetime.get_day_of_year()

    def get_day_of_week(self):
        return self._datetime.get_day_of_week()

    def get_hour(self):
        return self._datetime.get_hour()

    def get_minute(self):
        return self._datetime.get_minute()

    def get_second(self):
        return self._datetime.get_second()

    def get_nano(self):
        return self._datetime.get_nano()

    def with_adjuster(self, adjuster):
        if isinstance(adjuster, LocalDate) or isinstance(adjuster, LocalTime) or \
                isinstance(adjuster, LocalDateTime):
            return self.with_datetime_offset(self._datetime.with_adjuster(adjuster), self._offset)
        elif isinstance(adjuster, Instant):
            return self.of_instant(adjuster, self._offset)
        elif isinstance(adjuster, ZoneOffset):
            return self.with_datetime_offset(self._datetime, adjuster)
        elif isinstance(adjuster, OffsetDateTime):
            return adjuster
        return adjuster.adjust_into(self)

    def with_field(self, field, new_value):
        if isinstance(field, ChronoFieldItem):
            f = field
            if f == ChronoField.INSTANT_SECONDS:
                return self.of_instant(Instant.of_epoch_second(new_value, self.get_nano()), self._offset)
            elif f == ChronoField.OFFSET_SECONDS:
                return self.with_datetime_offset(self._datetime,
                                                 ZoneOffset.of_total_seconds(f.check_valid_int_value(new_value)))
            return self.with_datetime_offset(self._datetime.with_field(field, new_value), self._offset)
        return field.adjust_into(self, new_value)

    def with_year(self, year):
        return self.with_datetime_offset(self._datetime.with_year(year), self._offset)

    def with_month(self, month):
        return self.with_datetime_offset(self._datetime.with_month(month), self._offset)

    def with_day_of_month(self, day_of_month):
        return self.with_datetime_offset(self._datetime.with_day_of_month(day_of_month), self._offset)

    def with_day_of_year(self, day_of_year):
        return self.with_datetime_offset(self._datetime.with_day_of_year(day_of_year), self._offset)

    def with_hour(self, hour):
        return self.with_datetime_offset(self._datetime.with_hour(hour), self._offset)

    def with_minute(self, minute):
        return self.with_datetime_offset(self._datetime.with_minute(minute), self._offset)

    def with_second(self, second):
        return self.with_datetime_offset(self._datetime.with_second(second), self._offset)

    def with_nano(self, nano):
        return self.with_datetime_offset(self._datetime.with_nano(nano), self._offset)

    def truncated_to(self, unit):
        return self.with_datetime_offset(self._datetime.truncated_to(unit), self._offset)

    def plus_temporal(self, temporal_amount):
        return temporal_amount.add_to(self)

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            return self.with_datetime_offset(self._datetime.plus(amount_to_add, unit), self._offset)
        return unit.add_to(self, amount_to_add)

    def plus_years(self, years):
        return self.with_datetime_offset(self._datetime.plus_years(years), self._offset)

    def plus_months(self, months):
        return self.with_datetime_offset(self._datetime.plus_months(months), self._offset)

    def plus_weeks(self, weeks):
        return self.with_datetime_offset(self._datetime.plus_weeks(weeks), self._offset)

    def plus_days(self, days):
        return self.with_datetime_offset(self._datetime.plus_days(days), self._offset)

    def plus_hours(self, hours):
        return self.with_datetime_offset(self._datetime.plus_hours(hours), self._offset)

    def plus_minutes(self, minutes):
        return self.with_datetime_offset(self._datetime.plus_minutes(minutes), self._offset)

    def plus_seconds(self, seconds):
        return self.with_datetime_offset(self._datetime.plus_seconds(seconds), self._offset)

    def plus_nanos(self, nanos):
        return self.with_datetime_offset(self._datetime.plus_nanos(nanos), self._offset)

    def minus_temporal(self, temporal_amount):
        return temporal_amount.subtract_from(self)

    def minus(self, amount=None, unit=None):
        if amount == 0x8000000000000000L:
            return self.plus(0x7fffffffffffffffL, unit).plus(1, unit)
        else:
            return self.plus(-amount, unit)

    def minus_years(self, years_to_subtract):
        if years_to_subtract == 0x8000000000000000L:
            return self.plus_years(0x7fffffffffffffffL).plus_years(1)
        else:
            return self.plus_years(-years_to_subtract)

    def minus_months(self, months_to_subtract):
        if months_to_subtract == 0x8000000000000000L:
            return self.plus_months(0x7fffffffffffffffL).plus_months(1)
        else:
            return self.plus_months(-months_to_subtract)

    def minus_weeks(self, weeks_to_subtract):
        if weeks_to_subtract == 0x8000000000000000L:
            return self.plus_months(0x7fffffffffffffffL).plus_weeks(1)
        else:
            return self.plus_weeks(-weeks_to_subtract)

    def minus_days(self, days_to_subtract):
        if days_to_subtract == 0x8000000000000000L:
            return self.plus_days(0x7fffffffffffffffL).plus_days(1)
        else:
            return self.plus_days(-days_to_subtract)
    
    def minus_hours(self, hours_to_subtract):
        if hours_to_subtract == 0x8000000000000000L:
            return self.plus_hours(0x7fffffffffffffffL).plus_hours(1)
        else:
            return self.plus_hours(-hours_to_subtract)
        
    def minus_minutes(self, minutes_to_subtract):
        if minutes_to_subtract == 0x8000000000000000L:
            return self.plus_minutes(0x7fffffffffffffffL).plus_minutes(1)
        else:
            return self.plus_minutes(-minutes_to_subtract)
        
    def minus_seconds(self, seconds_to_subtract):
        if seconds_to_subtract == 0x8000000000000000L:
            return self.plus_seconds(0x7fffffffffffffffL).plus_seconds(1)
        else:
            return self.plus_seconds(-seconds_to_subtract)
        
    def minus_nanos(self, nanos_to_subtract):
        if nanos_to_subtract == 0x8000000000000000L:
            return self.plus_nanos(0x7fffffffffffffffL).plus_nanos(1)
        else:
            return self.plus_nanos(-nanos_to_subtract)

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.to_local_date().get_chronology()
        elif query == TemporalQueries.precision():
            return ChronoUnit.NANOS
        elif query == TemporalQueries.offset() or query == TemporalQueries.zone():
            return self.get_offset()
        return super(OffsetDateTime, self).query(query)

    def adjust_into(self, temporal):
        return temporal.with_field(ChronoField.OFFSET_SECONDS, self.get_offset().get_total_seconds()).\
            with_field(ChronoField.EPOCH_DAY, self.to_local_date().to_epoch_day()).\
            with_field(ChronoField.NANO_OF_DAY, self.to_local_time().to_nano_of_day())

    def period_until(self, end_temporal, unit):
        if not isinstance(end_temporal, OffsetDateTime):
            raise DateTimeException('Unable to calculate period between objects of two different types')
        if isinstance(unit, ChronoUnitItem):
            end = end_temporal
            end = end.with_offset_same_instant(self._offset)
            return self._datetime.period_until(end._datetime, unit)
        return unit.between(self, end_temporal)

    def at_zone_same_instant(self, zone):
        return ZonedDateTime.of_instant_ldt(self._datetime, self._offset, zone)

    def at_zone_similar_local(self, zone):
        return ZonedDateTime.of_local(self._datetime, zone, self._offset)

    def to_local_date_time(self):
        return self._datetime

    def to_local_date(self):
        return self._datetime.to_local_date()

    def to_local_time(self):
        return self._datetime.to_local_time()

    def to_offset_time(self):
        #return OffsetTime.of(self._datetime.to_local_time, self._offset)
        raise NotImplementedError()

    def to_zoned_date_time(self):
        return ZonedDateTime.of(self._datetime, self._offset)

    def to_instant(self):
        return self._datetime.to_instant(self._offset)

    def to_epoch_second(self):
        return self._datetime.to_epoch_second(self._offset)

    def __cmp__(self, other):
        if self.get_offset().__eq__(other.get_offset()):
            return self.to_local_date_time().__cmp__(other.to_local_date_time())
        comp = self.to_epoch_second().__cmp__(other.to_epoch_second())
        if comp == 0:
            comp = self.to_local_time().get_nano().__cmp__(other.to_local_time().get_nano())
            if comp == 0:
                comp = self.to_local_date_time().__cmp__(other.to_local_date_time())
        return comp

    def is_after(self, other):
        this_epoch_sec = self.to_epoch_second()
        other_epoch_sec = other.to_epoch_second()
        return this_epoch_sec > other_epoch_sec or \
               (this_epoch_sec == other_epoch_sec and
                   self.to_local_time().get_nano() > other.to_local_time().get_nano())

    def is_before(self, other):
        this_epoch_sec = self.to_epoch_second()
        other_epoch_sec = other.to_epoch_second()
        return this_epoch_sec < other_epoch_sec or \
               (this_epoch_sec == other_epoch_sec and
                   self.to_local_time().get_nano() < other.to_local_time().get_nano())

    def is_equal(self, other):
        return self.to_epoch_second() == other.to_epoch_second() and \
            self.to_local_time().get_nano() == other.to_local_time().get_nano()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, OffsetDateTime):
            return self._datetime == other._datetime and self._offset == other._offset
        return False

    def __hash__(self):
        return self._datetime.__hash__() ^ self._offset.__hash__()

    def __str__(self):
        return self._datetime.__str__() + self._offset.__str__()







    
    



