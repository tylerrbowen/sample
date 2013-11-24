from abc import ABCMeta, abstractmethod

from utils.bp.date_time_exception import DateTimeException
from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from utils.bp.local_date import LocalDate
from chrono_local_date import ChronoLocalDate
from chronology import Chronology


class ChronoDateImpl(DefaultInterfaceTemporalAccessor, ChronoLocalDate, Temporal, TemporalAdjuster):
    """
    A date expressed in terms of a standard year-month-day calendar system.
    This class is used by applications seeking to handle dates in non-ISO calendar systems.

    """
    __metaclass__ = ABCMeta

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            f = unit
            if f == ChronoUnit.DAYS:
                return self.plus_days(amount_to_add)
            elif f == ChronoUnit.WEEKS:
                return self.plus_days(amount_to_add * 7)
            elif f == ChronoUnit.MONTHS:
                return self.plus_months(amount_to_add)
            elif f == ChronoUnit.YEARS:
                return self.plus_years(amount_to_add)
            elif f == ChronoUnit.DECADES:
                return self.plus_years(amount_to_add * 10)
            elif f == ChronoUnit.CENTURIES:
                return self.plus_years(amount_to_add * 100)
            elif f == ChronoUnit.MILLENNIA:
                return self.plus_years(amount_to_add * 1000)
            raise DateTimeException(unit.get_name() + " not valid for chronology " + self.get_chronology().get_id())
        return self.get_chronology().ensure_chrono_local_date(unit.add_to(self, amount_to_add))

    @abstractmethod
    def plus_years(self, years_to_add):
        pass

    @abstractmethod
    def plus_months(self, months_to_add):
        pass

    def plus_weeks(self, weeks_to_add):
        return self.plus_days(weeks_to_add * 7)

    @abstractmethod
    def plus_days(self, days_to_add):
        pass

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
            return self.plus_weeks(0x7fffffffffffffffL).plus_weeks(1)
        else:
            return self.plus_weeks(-weeks_to_subtract)
    
    def minus_days(self, days_to_subtract):
        if days_to_subtract == 0x8000000000000000L:
            return self.plus_days(0x7fffffffffffffffL).plus_days(1)
        else:
            return self.plus_days(-days_to_subtract)

    def at_time(self, local_time):
        return Chronology.date_time(self, local_time)

    def period_until(self, end_temporal, unit):
        if not isinstance(end_temporal, ChronoLocalDate):
            raise DateTimeException('Unable to calculate period between objects of two different types')
        end = end_temporal
        if not self.get_chronology().__eq__(end.get_chronology()):
            raise DateTimeException('Unable to calculate period between two different chronologies')
        if isinstance(unit, ChronoUnitItem):
            return LocalDate.from_temporal(self).period_until(end, unit)
        return unit.between(self, end_temporal)

    def period_until_date(self, end_date):
        raise NotImplementedError('Not supported')

