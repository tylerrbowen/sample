from default_interface_temporal import DefaultInterfaceTemporal
from abc import ABCMeta
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
from utils.bp.chrono.chrono_local_date import ChronoLocalDate
from utils.bp.chrono.chronology import Chronology
from utils.bp.temporal.temporal_queries import TemporalQueries


class DefaultInterfaceChronoLocalDate(DefaultInterfaceTemporal, ChronoLocalDate):

    __metaclass__ = ABCMeta

    def get_era(self):
        return self.get_chronology().era_of(self.get(ChronoField.ERA))

    def is_leap_year(self):
        return self.get_chronology().is_leap_year(self.get_long(ChronoField.YEAR))

    def length_of_year(self):
        return 366 if self.is_leap_year() else 365

    def is_supported(self, field):
        if isinstance(field, ChronoFieldItem):
            return field.is_date_field()
        return field is not None and field.is_supported_by(self)

    def with_adjuster(self, adjuster):
        return self.get_chronology().ensure_chrono_local_date(super(DefaultInterfaceChronoLocalDate, self).\
            with_adjuster(adjuster))

    def plus_temporal(self, temporal_amount):
        return self.get_chronology().ensure_chrono_local_date(super(DefaultInterfaceChronoLocalDate, self).\
            plus_temporal(temporal_amount))

    def minus_temporal(self, temporal_amount):
        return self.get_chronology().ensure_chrono_local_date(super(DefaultInterfaceChronoLocalDate, self).\
            minus_temporal(temporal_amount))

    def minus(self, amount=None, unit=None):
        return self.get_chronology().ensure_chrono_local_date(super(DefaultInterfaceChronoLocalDate, self).\
            minus(amount, unit))

    def adjust_into(self, temporal):
        return temporal.with_field(ChronoField.EPOCH_DAY, self.to_epoch_day())

    def at_time(self, local_time):
        return Chronology.date_time(self, local_time)

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.get_chronology()
        return super(DefaultInterfaceChronoLocalDate, self).query(query)

    def to_epoch_day(self):
        return self.get_long(ChronoField.EPOCH_DAY)

    def __cmp__(self, other):
        comp = self.to_epoch_day().__cmp__(other.to_epoch_day())
        if comp == 0:
            comp = self.get_chronology().__cmp__(other.get_chronology())
        return comp

    def is_after(self, other):
        return self.to_epoch_day() > other.to_epoch_day()

    def is_before(self, other):
        return self.to_epoch_day() < other.to_epoch_day()

    def is_equal(self, other):
        return self.to_epoch_day() == other.to_epoch_day()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, DefaultInterfaceChronoLocalDate):
            return self.__cmp__(other) == 0
        return False

    def __hash__(self):
        ep_day = self.to_epoch_day()
        return self.get_chronology().__hash__() ^ (int(ep_day ^ (ep_day >> 32)))

    def __str__(self):
        yoe = self.get_long(ChronoField.YEAR_OF_ERA)
        moy = self.get_long(ChronoField.MONTH_OF_YEAR)
        dom = self.get_long(ChronoField.DAY_OF_MONTH)
        buf = ''
        buf += self.get_chronology().__str__()
        buf += ' '
        buf += self.get_era().__str__()
        buf += ' '
        buf += yoe.__str__()
        buf += '-0' if moy < 10 else '-'
        buf += moy.__str__()
        buf += '-0' if dom < 10 else '-'
        buf += dom.__str__()
        return buf.__str__()