from utils.bp.duration import Duration


class ZoneOffsetTransition(object):

    def __init__(self,
                 transition,
                 offset_before,
                 offset_after):
        self._transition = transition
        self._offset_before = offset_before
        self._offset_after = offset_after

    @classmethod
    def of(cls, transition, offset_before, offset_after):
        if offset_before.__eq__(offset_after):
            raise TypeError('offsets must not be equal')
        if transition.get_nano() != 0:
            raise TypeError('Nano-of-second must be zero')
        return ZoneOffsetTransition(transition, offset_before, offset_after)


    def get_instant(self):
        return self._transition.to_instant(self._offset_before)

    def to_epoch_second(self):
        return self._transition.to_epoch_second(self._offset_before)

    def get_datetime_before(self):
        return self._transition

    def get_datetime_after(self):
        return self._transition.plus_seconds(self.get_duration_seconds())

    def get_offset_before(self):
        return self._offset_before

    def get_offset_after(self):
        return self._offset_after

    def get_duration(self):
        return Duration.of_seconds(self.get_duration_seconds())

    def get_duration_seconds(self):
        return self.get_offset_after().get_total_seconds() - self.get_offset_before().get_total_seconds()

    def is_gap(self):
        return self.get_offset_after().get_total_seconds() > self.get_offset_before().get_total_seconds()

    def is_overlap(self):
        return self.get_offset_after().get_total_seconds() < self.get_offset_before().get_total_seconds()

    def is_valid_offset(self, offset):
        return False if self.is_gap() else self.get_offset_before().__eq__(offset) or self.get_offset_after().__eq__(offset)

    def get_valid_offsets(self):
        if self.is_gap():
            return []
        return [self.get_offset_before(), self.get_offset_after()]

    def __cmp__(self, other):
        return self.get_instant().__cmp__(other.get_instant())

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ZoneOffsetTransition):
            return self._transition.__eq__(other._transition) and \
                self._offset_after.__eq__(other._offset_after) and \
                self._offset_before.__eq__(other._offset_before)
        return False

    def __hash__(self):
        return self._transition.__hash__() ^ self._offset_before.__hash__() ^ self._offset_after.__hash__()

    def __str__(self):
        s = 'Transition['
        s += 'Gap' if self.is_gap() else 'Overlap'
        s += ' at '
        s += self._transition.__str__()
        s += self._offset_before.__str__()
        s += ' to '
        s += self._offset_after.__str__()
        s += ']'
        return s

