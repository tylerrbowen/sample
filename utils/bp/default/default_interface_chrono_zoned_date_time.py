

from default_interface_temporal import DefaultInterfaceTemporal
from abc import ABCMeta
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
from utils.bp.chrono.chrono_zoned_date_time import ChronoZonedDateTime
from utils.bp.chrono.chronology import Chronology
from utils.bp.date_time_exception import DateTimeException
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.local_date import LocalDate
from utils.bp.instant import Instant


class DefaultInterfaceChronoZonedDateTime(DefaultInterfaceTemporal, ChronoZonedDateTime):

    __metaclass__ = ABCMeta

    def range(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS or field == ChronoField.OFFSET_SECONDS:
                return field.range()
            return self.to_local_datetime().range(field)
        return field.range_refined_by(self)

    def get(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS:
                raise DateTimeException("Field too large for an int: " + field.get_name())
            elif field == ChronoField.OFFSET_SECONDS:
                return self.get_offset().get_total_seconds()
            return self.to_local_datetime().get(field)
        return super(DefaultInterfaceChronoZonedDateTime, self).get(field)

    def get_long(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.INSTANT_SECONDS:
                return self.to_epoch_second()
            elif field == ChronoField.OFFSET_SECONDS:
                return self.get_offset().get_total_seconds()
            return self.to_local_datetime().get_long(field)
        return field.get_from(self)

    def to_local_date(self):
        return self.to_local_datetime().to_local_date()

    def to_local_time(self):
        return self.to_local_datetime().to_local_time()

    def with_adjuster(self, adjuster):
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(
            super(DefaultInterfaceChronoZonedDateTime, self).with_adjuster(adjuster))

    def plus_temporal(self, temporal_amount):
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(
            super(DefaultInterfaceChronoZonedDateTime, self).plus_temporal(temporal_amount))

    def minus_temporal(self, temporal_amount):
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(
            super(DefaultInterfaceChronoZonedDateTime, self).minus_temporal(temporal_amount))

    def minus(self, amount=None, unit=None):
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(
            super(DefaultInterfaceChronoZonedDateTime, self).minus(amount, unit))

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.get_zone()
        elif query == TemporalQueries.precision():
            return ChronoUnit.NANOS
        elif query == TemporalQueries.offset():
            return self.get_offset()
        elif query == TemporalQueries.local_date():
            return LocalDate.of_epoch_day(self.to_local_date().to_epoch_day())
        elif query == TemporalQueries.local_time():
            return self.to_local_time()
        return super(DefaultInterfaceChronoZonedDateTime, self).query(query)

    def to_instant(self):
        return Instant.of_epoch_second(self.to_epoch_second(), self.to_local_time().get_nano())

    def to_epoch_second(self):
        epoch_day = self.to_local_date().to_epoch_day()
        secs = epoch_day * 86400 + self.to_local_time().to_second_of_day()
        secs -= self.get_offset().get_total_seconds()
        return secs

    def __cmp__(self, other):
        comp = self.to_epoch_second().__cmp__(other.to_epoch_second())
        if comp == 0:
            comp == self.to_local_time().get_nano() - other.to_local_time().get_nano()
            if comp == 0:
                comp = self.to_local_datetime().__cmp__(other.to_local_datetime())
        return comp

    def is_after(self, other):
        this_epoch_sec = self.to_epoch_second()
        other_epoch_sec = other.to_epoch_second()
        return this_epoch_sec > other_epoch_sec or \
               (this_epoch_sec == other_epoch_sec and self.to_local_time().get_nano() > other.to_local_time().get_nano())

    def is_before(self, other):
        this_epoch_sec = self.to_epoch_second()
        other_epoch_sec = other.to_epoch_second()
        return this_epoch_sec < other_epoch_sec or \
               (this_epoch_sec == other_epoch_sec and self.to_local_time().get_nano() < other.to_local_time().get_nano())

    def is_equal(self, other):
        return self.to_epoch_second() == other.to_epoch_second() and \
            self.to_local_time().get_nano() == other.to_local_time().get_nano()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ChronoZonedDateTime):
            return self.__cmp__(other) == 0
        return False

    def __hash__(self):
        return self.to_local_datetime().__hash__() ^ self.get_offset().__hash__() ^ self.get_zone().__hash__()

    def __str__(self):
        s = self.to_local_datetime().__str__() + self.get_offset().__str__()
        if self.get_offset() != self.get_zone():
            s += '[' + self.get_zone().__str__() + ']'
        return s


