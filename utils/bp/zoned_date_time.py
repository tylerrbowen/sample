from utils.bp.clock import Clock
from utils.bp.instant import Instant
from utils.bp.default.default_interface_chrono_zoned_date_time import DefaultInterfaceChronoZonedDateTime
from utils.bp.temporal.temporal import Temporal
from utils.bp.chrono.chrono_zoned_date_time import ChronoZonedDateTime
from local_date_time import LocalDateTime
from zone_offset import ZoneOffset


class ZonedDateTime(DefaultInterfaceChronoZonedDateTime, ChronoZonedDateTime):
    def __init__(self,
                 date_time,
                 offset,
                 zone):
        self._date_time = date_time
        self._offset = offset
        self._zone = zone

    def get_year(self):
        return self._date_time._date.get_year()

    def get_month(self):
        return self._date_time._date.get_month()

    def get_day_of_month(self):
        return self._date_time._date.get_day_of_month()

    @classmethod
    def now(cls, zone=None, clock=None):
        if clock is None:
            if zone is None:
                return cls.now(zone=Clock.system_default_zone())
            else:
                return cls.now(clock=Clock.system(zone))
        now = clock.instant()
        return cls.of_instant(now, clock.get_zone())

    @classmethod
    def of_instant(cls, instant, zone):
        return cls.create(instant.get_epoch_second(), instant.get_nano(), zone)

    @classmethod
    def of_instant_ldt(cls, local_date_time, offset, zone):
        return cls.create(local_date_time.to_epoch_second(offset), local_date_time.get_nano(), zone)

    @classmethod
    def create(cls, epoch_second, nano_of_second, zone):
        instant = Instant.of_epoch_second(epoch_second, nano_of_second)
        ldt = LocalDateTime.of_epoch_second(epoch_second, nano_of_second, ZoneOffset(0))
        return ZonedDateTime(ldt, ZoneOffset(0), zone)

    def get_offset(self):
        return self._offset

    def get_zone(self):
        return self._zone

    def is_supported(self, field):
        return False

    def period_until(self, end_temporal, unit):
        raise NotImplementedError()

    def plus_temporal(self, temporal_amount):
        raise NotImplementedError()

    def plus(self, amount_to_add=None, unit=None):
        raise NotImplementedError()

    def to_local_datetime(self):
        raise NotImplementedError()

    def with_adjuster(self, adjuster):
        raise NotImplementedError

    def with_field(self, field, new_value):
        raise NotImplementedError

    def with_earlier_offset_at_overlap(self):
        raise NotImplementedError

    def with_later_offset_at_overlap(self):
        raise NotImplementedError

    def with_zone_same_instant(self, zone_id):
        raise NotImplementedError

    def with_zone_same_local(self, zone_id):
        raise NotImplementedError

    def minus_temporal(self, temporal_amount):
        raise NotImplementedError

    def minus(self, amount=None, unit=None):
        raise NotImplementedError

    def is_after(self, other):
        return self._date_time._date.is_after(other._date_time._date)