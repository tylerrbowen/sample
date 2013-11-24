
from default_interface_temporal import DefaultInterfaceTemporal
from abc import ABCMeta
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
from utils.bp.chrono.chrono_local_date_time import ChronoLocalDateTime
from utils.bp.chrono.chronology import Chronology
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.local_date import LocalDate
from utils.bp.instant import Instant


class DefaultInterfaceChronoLocalDateTime(DefaultInterfaceTemporal, ChronoLocalDateTime):

    __metaclass__ = ABCMeta

    def with_adjuster(self, adjuster):
        return  self.to_local_date().get_chronology().ensure_chrono_local_date_time(
            super(DefaultInterfaceChronoLocalDateTime, self).with_adjuster(adjuster))

    def plus_temporal(self, temporal_amount):
        return self.to_local_date().get_chronology().ensure_chrono_local_date_time(
            super(DefaultInterfaceChronoLocalDateTime, self).plus_temporal(temporal_amount))

    def minus_temporal(self, temporal_amount):
        return self.to_local_date().get_chronology().ensure_chrono_local_date_time(
            super(DefaultInterfaceChronoLocalDateTime, self).minus_temporal(temporal_amount))

    def minus(self, amount=None, unit=None):
        return self.to_local_date().get_chronology().ensure_chrono_local_date_time(
            super(DefaultInterfaceChronoLocalDateTime, self).minus(amount, unit))

    def adjust_into(self, temporal):
        return temporal.with_field(ChronoField.EPOCH_DAY, self.to_local_date().to_epoch_day()).\
            with_field(ChronoField.NANO_OF_SECOND, self.to_local_time().to_nano_of_day())

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.to_local_date().get_chronology()
        elif query == TemporalQueries.precision():
            return ChronoUnit.NANOS
        elif query == TemporalQueries.local_date():
            return LocalDate.of_epoch_day(self.to_local_date())
        elif query == TemporalQueries.local_time():
            return self.to_local_time()
        return super(DefaultInterfaceChronoLocalDateTime, self).query(query)

    def to_instant(self, offset):
        return Instant.of_epoch_second(self.to_epoch_second(offset), self.to_local_time().get_nano())

    def to_epoch_second(self, offset):
        epoch_day = self.to_local_date().to_epoch_day()
        secs = epoch_day * 86400 + self.to_local_time().to_second_of_day()
        secs -= offset.get_total_seconds()
        return secs

    def __cmp__(self, other):
        comp = self.to_local_date().__cmp__(other.to_local_date())
        if comp == 0:
            comp = self.to_local_time().__cmp__(other.to_local_time())
            if comp == 0:
                comp = self.to_local_date().get_chronology().__cmp__(other.to_local_date().get_chronology())
        return comp

    def is_after(self, other):
        this_ep_day = self.to_local_date().to_epoch_day()
        other_ep_day = other.to_local_date().to_epoch_day()
        return this_ep_day > other_ep_day or \
               (this_ep_day == other_ep_day and self.to_local_time().to_nano_of_day() > other.to_local_time().to_nano_of_day())

    def is_before(self, other):
        this_ep_day = self.to_local_date().to_epoch_day()
        other_ep_day = other.to_local_date().to_epoch_day()
        return this_ep_day < other_ep_day or \
               (this_ep_day == other_ep_day and self.to_local_time().to_nano_of_day() < other.to_local_time().to_nano_of_day())

    def is_equal(self, other):
        return self.to_local_time().to_nano_of_day() == other.to_local_time().to_nano_of_day() and \
            self.to_local_date().to_epoch_day() == other.to_local_date().to_epoch_day()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ChronoLocalDateTime):
            return self.__cmp__(other) == 0
        return False

    def __hash__(self):
        return self.to_local_date().__hash__() ^ self.to_local_time().__hash__()

    def __str__(self):
        return self.to_local_date().__str__() + 'T' + self.to_local_time().__str__()



