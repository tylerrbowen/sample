from utils.bp.date_time_exception import DateTimeException
import datetime as dt
from utils.bp.local_time import LocalTime
from utils.bp.local_date import LocalDate
from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from temporal.temporal import Temporal
from temporal.temporal_adjuster import TemporalAdjuster
from chrono.chrono_local_date import ChronoLocalDate

from clock import Clock


class LocalDateTime(object): #DefaultInterfaceTemporalAccessor, Temporal, TemporalAdjuster, ChronoLocalDate):

    def __init__(self,
                 date,
                 time):
        self._date = date
        self._time = time

    @classmethod
    def MIN(cls):
        return LocalDateTime.of(LocalDate.MIN, LocalTime.MIN)

    @classmethod
    def MAX(cls):
        return LocalDateTime.of(LocalDate.MAX, LocalTime.MAX)

    @classmethod
    def now(cls, clock=None, zone=None):
        if clock is None and zone is None:
            return cls.now(Clock.system_default_zone())
        elif zone is None:
            return cls.now(Clock.system(zone))
        else:
            now = clock.instant()
            offset = clock.getZone().getRules().getOffset(now)
            return cls.of_epoch_second(now.get_epoch_second(), now.get_nano(), offset)

    @classmethod
    def of_epoch_second(cls, epoch_second, nano_of_second, offset):
        localSecond = epoch_second + offset.get_total_seconds()
        localEpochDay = localSecond // LocalTime.SECONDS_PER_DAY
        secsOfDay = localSecond // LocalTime.SECONDS_PER_DAY
        date = LocalDate.of_epoch_day(localEpochDay)
        time = LocalTime.of_second_of_day(secsOfDay, nano_of_second)
        return LocalDateTime(date, time)

    @classmethod
    def parse(cls, text, formatter=None):
        ld = LocalDate.parse(text)
        lt = LocalTime.parse(text)
        return LocalDateTime(ld, lt)

    @classmethod
    def of(cls, local_date, local_time):
        return LocalDateTime(local_date, local_time)

    def get_date(self):
        return self._date

    def get_time(self):
        return self._time

    def get_long(self, field):
        return self._time.get_long(field) if field.is_time_field() else self._date.get_long(field)


    def to_datetime(self):
        return dt.datetime(self.get_date().get_year(),
                           self.get_date().get_month(),
                           self.get_date().get_day(),
                           self.get_time().get_hour(),
                           self.get_time().get_minute(),
                           self.get_time().get_second(),
                           self.get_time().get_nano()*1000)

    def is_after(self, other):
        #if isinstance(other, LocalDateTime):
        return self._date.compare_to_0(other._date) > 0
        #raise Exception

    def to_epoch_mill(self):
        return self._date.to_epoch_mill()

    def __str__(self):
        return self._date.__str__() + ' ' + self._time.__str__()













