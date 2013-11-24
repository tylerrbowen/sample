__author__ = 'Tyler'

from abc import ABCMeta, abstractmethod
import datetime as dt

import pytz
import delorean

from utils.bp.instant import Instant
from utils.bp.duration import Duration
from utils.bp.zone_id import ZoneOffset, ZoneId
from utils.bp.local_time import LocalTime


class Clock(object):
    """
    A clock providing access to the current instant, date and time using a time-zone.
    """
    __metaclass__ = ABCMeta

    UTC_START = dt.datetime(1970, 1, 1, 0, 0, 0, 0, pytz.utc)

    @classmethod
    def system_utc(cls):
        return SystemClock(ZoneOffset.UTC())

    @classmethod
    def system_default_zone(cls):
        return SystemClock(ZoneId.system_default())

    @classmethod
    def system(cls, zone):
        return SystemClock(zone)

    @classmethod
    def tick_seconds(cls, zone):
        return TickClock(cls.system(zone), LocalTime.NANOS_PER_SECOND)

    @classmethod
    def tick_minutes(cls, zone):
        return TickClock(cls.system(zone), LocalTime.NANOS_PER_MINUTE)

    @classmethod
    def tick(cls, base_clock, tick_duration):
        if tick_duration.is_negative():
            raise Exception
        tick_nanos = tick_duration.to_nanos()
        if tick_nanos % 1000000 == 0:
            pass
        elif 1000000000 % tick_nanos == 0:
            pass
        else:
            raise TypeError('Invalid Tick Duration')
        if tick_nanos <= 1:
            return base_clock
        return TickClock(base_clock, tick_nanos)

    @classmethod
    def fixed(cls, fixed_instant, zone):
        return FixedClock(fixed_instant, zone)

    @classmethod
    def offset(cls, base_clock, offset_duration):
        return OffsetClock(base_clock, offset_duration)

    @abstractmethod
    def get_zone(self):
        pass

    @abstractmethod
    def with_zone(self, zone):
        pass

    def millis(self):
        return self.instant().to_epoch_milli()

    def instant(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        return super(self.__class__, self).__eq__(other)

    @abstractmethod
    def __hash__(self):
        return super(self.__class__, self).__hash__()


class SystemClock(Clock):
    def __init__(self, zone_id):
        self._zone = zone_id

    def get_zone(self):
        return self._zone

    def with_zone(self, zone):
        if zone.__eq__(self._zone):
            return self
        return SystemClock(zone)

    def millis(self):
        now = delorean.localize(dt.datetime.utcnow(),
                                'UTC')
        diff = now - self.UTC_START
        millis = (diff.days * 24 * 60 * 60 + diff.seconds) * 1000 + diff.microseconds / 1000.
        return millis

    def instant(self):
        return Instant.of_epoch_milli(self.millis())

    def __eq__(self, other):
        if isinstance(other, SystemClock):
            return self._zone.__eq__(other._zone)
        return False

    def __hash__(self):
        return self._zone.__hash__() + 1

    def __str__(self):
        return 'SystemClock[' + self._zone.__str__() + ']'


class FixedClock(Clock):
    def __init__(self,
                 fixed_instant,
                 zone_id):
        super(FixedClock, self).__init__()
        self._instant = fixed_instant
        self._zone = zone_id

    def get_zone(self):
        return self._zone

    def millis(self):
        return self._instant.to_epoch_millis()

    def instant(self):
        return self._instant

    def __eq__(self, other):
        if isinstance(other, FixedClock):
            return self._instant.__eq__(other._instant)
        return False

    def __hash__(self):
        return self._instant.__hash__() ^ self._zone.__hash__()

    def __str__(self):
        return 'FixedClock[' + self._instant.__str__() + ',' + self._zone.__str__() + ']'


class OffsetClock(Clock):
    def __init__(self,
                 base_clock,
                 offset):
        self._base_clock = base_clock
        self._offset = offset

    def get_zone(self):
        return self._base_clock.get_zone()

    def with_zone(self, zone_id):
        return OffsetClock(self._base_clock.with_zone(zone_id),
                           self._offset)

    def millis(self):
        return self._base_clock.millis() + self._offset.to_millis()

    def instant(self):
        return self._base_clock.instant().plus(self._offset)

    def __eq__(self, other):
        if isinstance(OffsetClock, other):
            return self._base_clock.__eq__(other._base_clock) and self._offset.__eq__(other._offset)
        return False

    def __hash__(self):
        return self._base_clock.__hash__() ^ self._offset.__hash__()

    def __str__(self):
        return 'OffsetClock[' + self._base_clock.__str__() + ',' + self._offset.__str__() + ']'


class TickClock(Clock):
    def __init__(self,
                 base_clock,
                 tick_nanos):
        super(Clock, self).__init__()
        self._base_clock = base_clock
        self._tick_nanos = tick_nanos

    def get_zone(self):
        return self._base_clock.get_zone()

    def with_zone(self, zone_id):
        return TickClock(self._base_clock.with_zone(zone_id),
                         self._tick_nanos)

    def millis(self):
        millis = self._base_clock.millis()
        return millis - divmod(millis, self._tick_nanos/1000000L)

    def instant(self):
        if self._tick_nanos % 1000000 == 0:
            millis = self._base_clock.millis()
            return Instant.of_epoch_milli(millis - divmod(millis, self._tick_nanos/1000000L))
        instant = self._base_clock.instant()
        nanos = instant.get_nano()
        adjust = divmod(nanos, self._tick_nanos)
        return instant.minus_nanos(adjust)

    def __eq__(self, other):
        if isinstance(TickClock, other):
            return self._base_clock.__eq__(other._base_clock) and self._tick_nanos == other._tick_nanos
        return False

    def __hash__(self):
        return self._base_clock.__hash__() ^ (self._tick_nanos ^ (self._tick_nanos + 32))

    def __str__(self):
        return 'TickClock[' + self._base_clock.__str__() + ', ' + Duration.of_nanos(self._tick_nanos).__str__() + ']'
