from abc import ABCMeta, abstractmethod
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from ids.comparable import Comparable

class ChronoZonedDateTimeComparator:
    def compare(self, datetime1, datetime2):
        comp = datetime1.to_epoch_second().__cmp__(datetime2.to_epoch_second())
        if comp == 0:
            comp = datetime1.to_local_time().to_nano_of_day().__cmp__(datetime2.to_local_time().to_nano_of_day())
            return comp
        return comp


class ChronoZonedDateTime(Temporal, Comparable):
    """
    A date-time with a time-zone in an arbitrary chronology,
    intended for advanced globalization use cases.
    """
    __metaclass__ = ABCMeta

    INSTANT_COMPARATOR = ChronoZonedDateTimeComparator()

    @abstractmethod
    def to_local_date(self):
        pass

    @abstractmethod
    def to_local_time(self):
        pass

    @abstractmethod
    def to_local_datetime(self):
        pass

    @abstractmethod
    def get_offset(self):
        pass

    @abstractmethod
    def get_zone(self):
        pass

    @abstractmethod
    def with_earlier_offset_at_overlap(self):
        pass

    @abstractmethod
    def with_later_offset_at_overlap(self):
        pass

    @abstractmethod
    def with_zone_same_local(self, zone_id):
        pass

    @abstractmethod
    def with_zone_same_instant(self, zone_id):
        pass

    @abstractmethod
    def with_adjuster(self, adjuster):
        pass

    @abstractmethod
    def with_field(self, field, new_value):
        pass

    @abstractmethod
    def plus(self, amount_to_add=None, unit=None):
        pass

    @abstractmethod
    def plus_temporal(self, temporal_amount):
        pass

    @abstractmethod
    def minus(self, amount=None, unit=None):
        pass

    @abstractmethod
    def minus_temporal(self, temporal_amount):
        pass

    @abstractmethod
    def to_instant(self):
        pass

    @abstractmethod
    def to_epoch_second(self):
        pass

    @abstractmethod
    def __cmp__(self, other):
        pass

    @abstractmethod
    def is_before(self, other):
        pass

    @abstractmethod
    def is_after(self, other):
        pass

    @abstractmethod
    def is_equal(self, other):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass



