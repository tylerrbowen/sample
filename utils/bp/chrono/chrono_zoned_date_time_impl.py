from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from utils.bp.date_time_exception import DateTimeException
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.temporal.chrono_field import ChronoField, ChronoFieldItem
from utils.bp.local_date_time import LocalDateTime
from chrono_zoned_date_time import ChronoZonedDateTime



class ChronoZonedDateTimeImpl(DefaultInterfaceTemporalAccessor, ChronoZonedDateTime):
    """
    A date-time with a time-zone in the calendar neutral API.
    date_time
    offset
    zone
    """
    def __init__(self,
                 date_time,
                 offset,
                 zone):
        self._date_time = date_time
        self._offset = offset
        self._zone = zone

    @classmethod
    def of_best(cls, local_date_time, zone, preferred_offset):
        """
        Obtains an instance from a local date-time using the preferred offset if possible.
        @param localDateTime  ChronoLocalDateTimeImpl: the local date-time, not null
        @param zone:  ZoneId: the zone identifier, not null
        @param preferredOffset: ZoneOffset:  the zone offset, null if no preference
        @return the zoned date-time, not null
        """
        if isinstance(zone, ZoneOffset):
            return ChronoZonedDateTimeImpl(local_date_time, zone, zone)
        rules = zone.get_rules()
        iso_LDT = LocalDateTime.from_temporal(local_date_time)
        valid_offsets = rules.get_valid_offsets(iso_LDT)
        if len(valid_offsets) == 1:
            offset = valid_offsets[0]
        elif len(valid_offsets) == 0:
            trans = rules.get_transition(iso_LDT)
            local_date_time = local_date_time.plus_seconds(trans.get_duration().get_seconds())
            offset = trans.get_offset_after()
        else:
            if preferred_offset is not None and preferred_offset in valid_offsets:
                offset = preferred_offset
            else:
                offset = valid_offsets[0]
        assert offset is not None
        return ChronoZonedDateTimeImpl(local_date_time, offset, zone)

    @classmethod
    def of_instant(cls, chrono, instant, zone):
        rules = zone.get_rules()
        offset = rules.get_offset(instant)
        assert offset is not None
        ldt = LocalDateTime.of_epoch_second(instant.get_epoch_second(), instant.get_nano(), offset)
        cldt = chrono.local_date_time(ldt)
        return ChronoZonedDateTimeImpl(cldt, offset, zone)

    def create(self, instant, zone):
        return self.of_instant(self.to_local_date().get_chronology(), instant, zone)

    def get_offset(self):
        return self._offset

    def with_earlier_offset_at_overlap(self):
        trans = self.get_zone().get_rules().get_transition(LocalDateTime.from_temporal(self))
        if trans is not None and trans.is_overlap():
            earlier_offset = trans.get_offset_before()
            if not earlier_offset.__eq___(self._offset):
                return ChronoZonedDateTimeImpl(self._date_time, earlier_offset, self._zone)
        return self

    def with_later_offset_at_overlap(self):
        trans = self.get_zone().get_rules().get_transition(LocalDateTime.from_temporal(self))
        if trans is not None:
            offset = trans.get_offset_after()
            if not offset.__eq__(self.get_offset()):
                return ChronoZonedDateTimeImpl(self._date_time, offset, self._zone)
        return self

    def to_local_datetime(self):
        return self._date_time

    def get_zone(self):
        return self._zone

    def with_zone_same_local(self, zone_id):
        return self.of_best(self._date_time, zone_id, self._offset)

    def with_zone_same_instant(self, zone_id):
        assert zone_id is not None
        return self if self._zone.__eq__(zone_id) else self.create(self._date_time.to_instant(self._offset), zone_id)

    def is_supported(self, field):
        return isinstance(field, ChronoFieldItem) or (field != None and field.is_support_by(self))

    def with_field(self, field, new_value):
        if isinstance(field, ChronoFieldItem):
            f = field
            if f == ChronoField.INSTANT_SECONDS:
                return self.plus(new_value - self.to_epoch_second(), ChronoUnit.SECONDS)
            elif f == ChronoField.OFFSET_SECONDS:
                offset = ZoneOffset.of_total_seconds(f.check_valid_int_value(new_value))
                return self.create(self._date_time.to_instant(offset), self._zone)
            return self.of_best(self._date_time.with_field(field, new_value), self._zone, self._offset)
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(field.adjust_into(self, new_value))

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            return self.with_adjuster(self._date_time.plus(amount_to_add, unit))
        return self.to_local_date().get_chronology().ensure_chrono_zoned_date_time(unit.add_to(self, amount_to_add))

    def period_until(self, end_temporal, unit):
        if not isinstance(end_temporal, ChronoZonedDateTime):
            raise DateTimeException('Unable to calculate period between objects of two different types')
        end = end_temporal
        if not self.to_local_date().get_chronology().__eq__(end.to_local_date().get_chronology()):
            raise DateTimeException('Unable to calculate period between two different chronologies')
        if isinstance(unit, ChronoUnitItem):
            end = end.with_zone_same_instant(self._offset)
            return self._date_time.period_until(end.to_local_datetime(), unit)
        return unit.between(self, end_temporal)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ChronoZonedDateTime):
            return self.__cmp__(other) == 0
        return False

    def __hash__(self):
        return self.to_local_datetime().__hash__() ^ self.get_offset().__hash__() ^ (self.get_zone().__hash__())

    def __str__(self):
        s = self.to_local_datetime().__str__() + self.get_offset().__str__()
        if self.get_offset() != self.get_zone():
            s += '[' + self.get_zone().__str__() + ']'
        return s


