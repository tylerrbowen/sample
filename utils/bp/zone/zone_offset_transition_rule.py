from utils.bp.local_date import LocalDate
from utils.bp.local_date_time import LocalDateTime
from zone_offset_transition import ZoneOffsetTransition
from utils.bp.chrono.iso_chronology import IsoChronology


class ZoneOffsetTransitionRule(object):

    def __init__(self,
                 month,
                 day_of_month_indicator,
                 day_of_week,
                 time,
                 time_end_of_day,
                 time_definition,
                 standard_offset,
                 offset_before,
                 offset_after):
        self.month = month
        self.dom = day_of_month_indicator
        self.dow = day_of_week
        self.time = time
        self.time_end_of_day = time_end_of_day
        self.time_definition = time_definition
        self.standard_offset = standard_offset
        self.offset_before = offset_before
        self.offset_after = offset_after

    def get_month(self):
        return self.month

    def get_day_of_month(self):
        return self.dom

    def get_day_of_week(self):
        return self.dow

    def get_local_time(self):
        return self.time

    def is_midnight_end_of_day(self):
        return self.time_end_of_day

    def get_time_definition(self):
        return self.time_definition

    def get_standard_offset(self):
        return self.standard_offset

    def get_offset_before(self):
        return self.offset_before

    def get_offset_after(self):
        return self.offset_after

    def create_transition(self, year):
        if self.dom < 0:
            date = LocalDate.of(year, self.month, self.month.length(IsoChronology.INSTANCE().is_leap_year(year)) + 1 + self.dom)
            if self.dow is not None:
                date = date.with_temporal(self.previous_or_same(self.dow))
        else:
            date = LocalDate.of(year, self.month, self.dom)
            if self.dow is not None:
                date = date.with_temporal(self.next_or_same(self.dow))
        if self.time_end_of_day:
            date = date.plus_days(1)
        local_dt = LocalDateTime.of(date, self.time)
        transition = self.time_definition.create_date_time(local_dt, self.standard_offset, self.offset_before)
        return ZoneOffsetTransition(transition, self.offset_before, self.offset_after)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ZoneOffsetTransitionRule):
            return self.month == other.month and \
                self.dom == other.dom and \
                self.dow == other.dow and \
                self.time_definition == other.time_definition and \
                self.time == other.time and \
                self.time_end_of_day == other.time_end_of_day and \
                self.standard_offset == other.standard_offset and \
                self.offset_after == other.offset_after and \
                self.offset_before == other.offset_before
        return False

    def __hash__(self):
        h = (self.time.to_second_of_day() + (1 if self.time_end_of_day else 0)) << 15
        h += (self.month.ordinal() << 11) + ((self.dom + 32) << 5)
        h += (7 if self.dow is None else self.dow.ordinal()) << 2
        h += self.time_definition().ordinal()
        h ^= self.standard_offset.__hash__() ^ self.offset_before.__hash__() ^ self.offset_after.__hash__()
        return h

    def __str__(self):
        return 'Transition Rule'

