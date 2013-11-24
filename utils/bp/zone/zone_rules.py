import numpu as np
from abc import ABCMeta, abstractmethod
from utils.bp.duration import Duration


class ZoneRules(object):
    """
    The rules defining how the zone offset varies for a single time-zone.
    The rules model all the historic and future transitions for a time-zone.
    {@link ZoneOffsetTransition} is used for known transitions, typically historic.
    {@link ZoneOffsetTransitionRule} is used for future transitions that are based
    on the result of an algorithm.
    The rules are loaded via {@link ZoneRulesProvider} using a {@link ZoneId}.
    The same rules may be shared internally between multiple zone IDs.

    """

    __metaclass__ = ABCMeta

    @classmethod
    def of(cls,
           base_standard_offset,
           base_wall_offset,
           standard_offset_transition_list,
           transition_list,
           last_rules):
        return StandardZoneRules(base_standard_offset,
                                 base_wall_offset,
                                 standard_offset_transition_list,
                                 transition_list,
                                 last_rules)

    @classmethod
    def of_offset(cls, offset):
        return Fixed(offset)

    @abstractmethod
    def is_fixed_offset(self):
        pass

    @abstractmethod
    def get_offset_instant(self, instant):
        pass

    @abstractmethod
    def get_offset_local_datetime(self, local_datetime):
        pass

    @abstractmethod
    def get_valid_offsets(self, local_datetime):
        pass

    @abstractmethod
    def get_transition(self, local_datetime):
        pass

    @abstractmethod
    def get_standard_offset(self, instant):
        pass

    @abstractmethod
    def get_daylight_savings(self, instant):
        pass

    @abstractmethod
    def is_daylight_savings(self, instant):
        pass

    @abstractmethod
    def is_valid_offset(self, local_datetime, offset):
        pass

    @abstractmethod
    def next_transition(self, instant):
        pass

    @abstractmethod
    def previous_transition(self, instant):
        pass

    @abstractmethod
    def get_transitions(self):
        pass

    @abstractmethod
    def get_transition_rules(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass




class Fixed(ZoneRules):

    def __init__(self, offset):
        self._offset = offset

    def is_fixed_offset(self):
        return True

    def get_offset_instant(self, instant):
        return self._offset

    def get_offset_local_datetime(self, local_datetime):
        return self._offset

    def get_valid_offsets(self, local_datetime):
        return [self._offset]

    def get_transition(self, local_datetime):
        return None

    def is_valid_offset(self, local_datetime, offset):
        return self._offset.__eq__(offset)

    def get_standard_offset(self, instant):
        return self._offset

    def get_daylight_savings(self, instant):
        return Duration.ZERO()

    def is_daylight_savings(self, instant):
        return False

    def next_transition(self, instant):
        return None

    def previous_transition(self, instant):
        return None

    def get_transition_rules(self):
        return []

    def get_transitions(self):
        return []

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Fixed):
            return self._offset.__eq__(other._offset)
        return False

    def __hash__(self):
        return self._offset.__hash__() + 1



class StandardZoneRules(ZoneRules):

    LAST_CACHED_YEAR = 2100

    def __init__(self,
                 base_standard_offset,
                 base_wall_offset,
                 standard_offset_transition_list,
                 transition_list,
                 last_rules):
        self._standard_transitions = []
        self._standard_offsets = [base_standard_offset]
        for sot in standard_offset_transition_list:
            self._standard_transitions.append(sot.to_epoch_second())
            self._standard_offsets.append(sot.get_offset_after())

        local_transition_list = []
        local_transition_offset_list = []
        local_transition_offset_list.append(base_wall_offset)

        for trans in transition_list:
            if trans.is_gap():
                local_transition_list.append(trans.get_datetime_before())
                local_transition_list.append(trans.get_datetime_after())
            else:
                local_transition_list.append(trans.get_datetime_before())
                local_transition_list.append(trans.get_datetime_after())
            local_transition_offset_list.append(trans.get_offset_after())

        self._savings_local_transitions = local_transition_list
        self._wall_offsets = local_transition_offset_list

        self._savings_instant_transitions = []
        for t in transition_list:
            self._savings_instant_transitions.append(t.get_instant().to_epoch_second())

        if len(last_rules) > 15:
            raise TypeError('too many transition rules')

        self._last_rules = last_rules
        self._last_rules_cache = dict()

    def is_fixed_offset(self):
        return len(self._savings_instant_transitions) == 0

    def get_offset_instant(self, instant):
        epoc_sec = instant.get_epoch_second()
        if len(self._last_rules) > 0 and \
                epoc_sec > self._savings_instant_transitions[-1]:
            year = self.find_year(epoc_sec, self._wall_offsets[-1])
            trans_array = self.find_transition_array(year)
            trans = None
            for i in range(len(trans_array)):
                trans = trans_array[i]
                if epoc_sec < trans.to_epoch_second():
                    return trans.get_offset_before()
            return trans.get_offset_after()
        index = self._savings_instant_transitions.index(epoc_sec)
        if index < 0:
            index = -index - 2
        return self._wall_offsets[index + 1]

    def get_offset_local_datetime(self, local_datetime):
        info = self.get_offset_inf(local_datetime)
        if isinstance(info, ZoneOffsetTransition):
            return info.get_offset_before()
        return info

    def get_valid_offsets(self, local_datetime):
        info = self.get_offset_info(local_datetime)
        if isinstance(info, ZoneOffsetTransition):
            return info.get_valid_offsets()
        return [info]

    def get_transition(self, local_datetime):
        info = self.get_offset_info(local_datetime)
        return info if isinstance(info, ZoneOffsetTransition) else None

    def get_offset_info(self, ldt):
        if len(self._last_rules) > 0 and \
                    ldt.is_after(self._savings_instant_transitions[-1]):
            trans_array = self.find_transition_array(ldt.get_year())
            info = None
            for trans in trans_array:
                info = self.find_offset_info(ldt, trans)
                if isinstance(info, ZoneOffsetTransition) or info.__eq__(trans.get_offset_before()):
                    return info

            return info
        index = self._savings_instant_transitions[ldt]
        if index == -1:
            return self._wall_offsets[0]
        if index < 0:
            index = -index -2
        elif index < len(self._savings_local_transitions)-1 and \
                self._savings_instant_transitions[index].__eq__(self._savings_instant_transitions[index+1]):
            index += 1
        if (index & 1) == 0:
            dt_before = self._savings_local_transitions[index]
            dt_after = self._savings_local_transitions[index+1]
            offset_before = self._wall_offsets[index / 2]
            offset_after = self._wall_offsets[index /2 +1]
            if offset_after.get_total_seconds() > offset_before.get_total_seconds():
                return ZoneOffsetTransition(dt_before, offset_before, offset_after)
            else:
                return ZoneOffsetTransition(dt_after, offset_before, offset_after)
        else:
            return self._wall_offsets[index /2 +1]

    def find_offset_info(self, ldt, trans):
        local_transition = trans.get_datetime_before()
        if trans.is_gap():
            if ldt.is_before(local_transition):
                return trans.get_offset_before()
            if ldt.is_before(trans.get_datetime_after()):
                return trans
            else:
                return trans.get_offset_after()
        else:
            if not ldt.is_before(local_transition):
                return trans.get_offset_after()
            if ldt.is_before(trans.get_datetime_after()):
                return trans.get_offset_before()
            else:
                return trans

    def is_valid_offset(self, local_datetime, offset):
        return offset in self.get_valid_offsets(local_datetime)

    def find_transition_array(self, year):
        year_obj = year
        trans_array = self._last_rules_cache.get(year_obj)
        if trans_array is not None:
            return trans_array
        rule_array = self._last_rules
        trans_array = []
        for i in range(len(rule_array)):
            trans_array.append(rule_array[i].create_transition(year))
        if year < self.LAST_CACHED_YEAR:
            self._last_rules_cache[year_obj] = trans_array
        return trans_array

    def get_standard_offset(self, instant):
        epoch_sec = instant.get_epoch_second()
        index = self._standard_transitions.index(epoch_sec)
        if index < 0:
            index = -index -2
        return self._standard_offsets[index + 1]

    def get_daylight_savings(self, instant):
        standard_offset = self.get_standard_offset(instant)
        actual_offset = self.get_offset(instant)
        return Duration.of_seconds(actual_offset.get_total_seconds() - standard_offset.get_total_seconds())

    def is_daylight_savings(self, instant):
        return not self.get_standard_offset(instant).__eq__(self.get_offset(instant))

    def next_transition(self, instant):
        epoch_sec = instant.get_epoch_second()
        if epoch_sec >= self._savings_instant_transitions[-1]:
            if len(self._last_rules) == 0:
                return None
            year = self.find_year(epoch_sec, self._wall_offsets[-1])
            trans_array = self.find_transition_array(year)
            for trans in trans_array:
                if epoch_sec <= trans.to_epoch_second():
                    return trans

            if year < Year.MAX_VALUE:
                trans_array = self.find_transition_array(year + 1)
                return trans_array[0]

            return None
        index = self._savings_instant_transitions.index(epoch_sec)
        if index < 0:
            index = -index -1
        else:
            index += 1
            return ZoneOffsetTransition(self._savings_instant_transitions[index],
                                        self._wall_offsets[index],
                                        self._wall_offsets[index+1])

    def previous_transition(self, instant):
        epoch_sec = instant.get_epoch_second()
        if instant.get_nano() > 0 and epoch_sec < 0x7fffffffffffffffL:
            epoch_sec += 1
        last_historic = self._savings_instant_transitions[-1]
        if len(self._last_rules) > 0 and epoch_sec > last_historic:
            last_historic_offset = self._wall_offsets[-1]
            year = self.find_year(epoch_sec, last_historic_offset)
            trans_array = self.find_transition_array(year)
            for i in range(len(trans_array)):
                if epoch_sec > trans_array[i].to_epoch_seconds():
                    return trans_array[i]
            last_historic_year = self.find_year(last_historic, last_historic_offset)
            year -= 1
            if year > last_historic_year:
                trans_array = self.find_transition_array(year)
                return trans_array[-1]
        index = self._savings_instant_transitions.index(epoch_sec)
        if index < 0:
            index = -index -1
        if index <= 0:
            return None
        return ZoneOffsetTransition(self._savings_instant_transitions[index-1],
                                    self._wall_offsets[index-1],
                                    self._wall_offsets[index])

    def find_year(self, epoch_second, offset):
        local_second = epoch_second + offset.get_total_seconds()
        local_epoch_day = local_epoch_day // 86400
        return LocalDate.of_epoch_day(local_epoch_day).get_year()

    def get_transition_rules(self):
        return self._last_rules

    def get_transitions(self):
        lst = []
        for i in range(len(self._savings_instant_transitions)):
            lst.append(ZoneOffsetTransition(self._savings_instant_transitions[i],
                                            self._wall_offsets[i],
                                            self._wall_offsets[i+1]))
        return lst

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, StandardZoneRules):
            return np.all(self._standard_transitions == other._standard_transitions) and \
                    np.all(self._standard_offsets == other._standard_offsets) and \
                    np.all(self._savings_instant_transitions == other._savings_instant_transitions) and \
                    np.all(self._wall_offsets == other._wall_offsets) and \
                    np.all(self._last_rules == other._last_rules)
        return False

    def __hash__(self):
        h = 0
        for s in self._standard_transitions:
            h ^= s.__hash__()
        for s in self._standard_offsets:
            h ^= s.__hash__()
        for s in self._savings_instant_transitions:
            h ^= s.__hash__()
        for s in self._wall_offsets:
            h ^= s.__hash__()
        for s in self._last_rules:
            h ^= s.__hash__()
        return h

    def __str__(self):
        return 'StandardZoneRules[currentStandardOffset=' + \
            self._standard_offsets[-1].__str__() + ']'


