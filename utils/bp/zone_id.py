import re

import numpy as np
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.temporal.temporal_accessor import TemporalAccessor
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster
from utils.bp.date_time_exception import DateTimeException
from ids.comparable import Comparable

from abc import ABCMeta, abstractmethod


class ZoneId(object):
    """
    A time-zone ID, such as {@code Europe/Paris}.

    """
    __metaclass__ = ABCMeta


    @classmethod
    def system_default(cls):
        return ZoneId.of('US/Central', cls.OLD_IDS_POST_2005)


    OLD_IDS_POST_2005 = {
        'US/Central': 'US/Central',
        'US/Eastern': 'US/Eastern',
        'US/Pacific': 'US/Pacific',
        'Europe/London': 'Europe/London',
        'EST': '-05:00',
        'CST': '-06:00',
        'MST': '-07:00',
        'PST': '-08:00',
        'HST': '-10:00',
    }

    @classmethod
    def of(cls, zone_id, alias_map=None):
        if alias_map is not None:
            string_id = alias_map.get(zone_id)
            if string_id is not None:
                string_id = string_id
            else:
                string_id = zone_id
            return cls.of(string_id)
        if len(zone_id) <= 1 or zone_id[0] == '+' or zone_id[0] == '-':
            return ZoneOffset.of(zone_id)
        elif zone_id[:2] == 'UTC' or zone_id[:3] == 'GMT':
            if len(zone_id) == 3 or (len(zone_id) == 4 and zone_id[3] == '0'):
                return ZoneOffset.UTC()
        return ZoneRegion.of_Id(zone_id, True)

    @classmethod
    def from_temporal(cls, temporal):
        obj = temporal.query(TemporalQueries.zone())
        if obj is None:
            raise Exception
        return obj

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_rules(self):
        pass


    def get_display_name(self):
        return self.__str__()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(ZoneId, other):
            return self.get_id() == other.get_id()
        return False

    def __hash__(self):
        return self.get_id().__hash__()

    def __str__(self):
        return self.get_id().__str__()

    def write(self, out):
        pass


class ZoneOffset(ZoneId, TemporalAccessor, TemporalAdjuster, Comparable):
    def __init__(self, total_seconds):
        self.total_seconds = total_seconds
        self.id = ZoneOffset.build_id(total_seconds)

    SECONDS_CACHE = dict()
    ID_CACHE = dict()
    SECONDS_PER_HOUR = 60 * 60
    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HOUR = 60
    MAX_SECONDS = 18 * SECONDS_PER_HOUR

    @classmethod
    def UTC(cls):
        return ZoneOffset.of_total_seconds(0)

    @classmethod
    def MIN(cls):
        return ZoneOffset.of_total_seconds(-cls.MAX_SECONDS)

    @classmethod
    def MAX(cls):
        return ZoneOffset.of_total_seconds(cls.MAX_SECONDS)

    @classmethod
    def of_offset_id(cls, offset_id):
        offset = cls.ID_CACHE.get(offset_id)
        if offset is not None:
            return offset
        # parse - +h, +hh, +hhmm, +hh:mm, +hhmmss, +hh:mm:ss
        if len(offset_id) == 2:
            offset_id = offset_id[0] + '0' + offset_id[1]
        if len(offset_id) == 3:
            hours = int(offset_id[1])
            minutes = 0
            seconds = 0
        elif len(offset_id) == 5:
            hours = int(offset_id[1])
            minutes = int(offset_id[3])
            seconds = 0
        elif len(offset_id) == 6:
            hours = int(offset_id[1])
            minutes = int(offset_id[4])
            seconds = 0
        elif len(offset_id) == 7:
            hours = int(offset_id[1])
            minutes = int(offset_id[3])
            seconds = int(offset_id[5])
        elif len(offset_id) == 9:
            hours = int(offset_id[1])
            minutes = int(offset_id[4])
            seconds = int(offset_id[7])
        else:
            raise Exception('Invalid ID')
        first_ch = offset_id[0]
        if first_ch != '+' and first_ch != '-':
            raise Exception('Invalid ID')
        if first_ch == '-':
            return cls.of_hours_minutes_seconds(-hours, -minutes, -seconds)
        else:
            return cls.of_hours_minutes_seconds(hours, minutes, seconds)

    @classmethod
    def parse_number(cls, offset_id, pos, preceded_by_colon):
        if preceded_by_colon and offset_id[pos-1] != ':':
            raise Exception('Invalid Id')
        ch1 = offset_id[pos]
        ch2 = offset_id[pos + 1]
        if ch1 < '0' or ch1 > '9' or ch2 < '0' or ch2 > '9':
            raise Exception('Invalid Id')
        return (int(ch1) - 48) * 10 + (int(ch2) - 48)

    @classmethod
    def of_hours(cls, hours):
        return cls.of_hours_minutes_seconds(hours, 0, 0)

    @classmethod
    def of_hours_minutes(cls, hours, minutes):
        return cls.of_hours_minutes_seconds(hours, minutes, 0)

    @classmethod
    def of_hours_minutes_seconds(cls, hours, minutes, seconds):
        total_seconds = cls.total_seconds(hours, minutes, seconds)
        return cls.of_total_seconds(total_seconds)

    @classmethod
    def from_temporal(cls, temporal):
        offset = temporal.query(TemporalQueries.offset())
        if offset is not None:
            raise Exception('Unable to obtain')
        return offset

    @classmethod
    def validate(cls, hours, minutes, seconds):
        if hours < -18 or hours > 18:
            raise DateTimeException('Zone offset hours not in valid range')
        if hours > 0:
            if minutes < 0 or seconds < 0:
                raise DateTimeException('Zone offset minutes and seconds must be negative because hours is negative')
        elif hours < 0:
            if minutes > 0 or seconds > 0:
                raise DateTimeException('Zone offset minutes and seconds must be negative because hours is negative')
        elif ((minutes > 0 and seconds < 0) or (minutes < 0 and seconds > 0)):
            raise DateTimeException('Zone offset minutes and seconds must be negative because hours is negative')
        if abs(minutes) > 59:
            raise DateTimeException('Zone offset minutes not in valid range')
        if abs(seconds) > 59:
            raise DateTimeException('Zone offset seconds not in valid range')
        if abs(hours) == 18 and (abs(minutes) > 0 or abs(seconds) > 0):
            raise DateTimeException('Zone offset seconds not in valid range')

    @classmethod
    def total_seconds(cls, hours, minutes, seconds):
        return hours*cls.SECONDS_PER_HOUR + \
               minutes*cls.SECONDS_PER_MINUTE + seconds

    @classmethod
    def of_total_seconds(cls, total_seconds):
        if np.abs(total_seconds) > cls.MAX_SECONDS:
            raise Exception('zone not in range')
        if np.mod(total_seconds, 15*cls.SECONDS_PER_MINUTE) == 0:
            total_secs = int(total_seconds)
            result = cls.SECONDS_CACHE.get(total_secs)
            if result is None:
                result = ZoneOffset(total_seconds)
                cls.SECONDS_CACHE[total_secs] = result
                result = cls.SECONDS_CACHE.get(total_secs)
                cls.ID_CACHE[result.get_id()] = result
            return result
        else:
            return ZoneOffset(total_seconds)

    @classmethod
    def build_id(cls, total_seconds):
        if total_seconds == 0:
            return 'Z'
        else:
            abs_total_seconds = np.abs(total_seconds)
            abs_hours = abs_total_seconds/cls.SECONDS_PER_HOUR
            abs_minutes = np.mod(abs_total_seconds/cls.SECONDS_PER_MINUTE,
                                 cls.MINUTES_PER_HOUR)
            return_string = ''
            if total_seconds < 0:
                return_string += '-'
            else:
                return_string += '+'
            if abs_hours < 10:
                return_string += '0' + str(abs_hours)
            else:
                return_string += '' + str(abs_hours)
            if abs_minutes < 10:
                return_string += '0' + str(abs_minutes)
            else:
                return_string += '' + str(abs_minutes)
            abs_seconds = np.mod(abs_total_seconds, cls.SECONDS_PER_MINUTE)
            if abs_seconds != 0:
                if abs_seconds < 10:
                    return_string += '0' + str(abs_seconds)
                else:
                    return_string += '' + str(abs_seconds)
            return return_string

    def get_total_seconds(self):
        return self.total_seconds

    def get_id(self):
        return self.id

    def get_rules(self):
        #return ZoneRules.of(self)
        pass

    def __cmp__(self, other):
        return 0

    def adjust_into(self, temporal):
        pass

    def get(self, field):
        pass

    def get_display_name(self):
        pass

    def get_long(self, field):
        pass

    def is_supported(self, field):
        return False

    def range(self, field):
        pass




class ZoneRegion(ZoneId):

    PATTERN = re.compile('[A-Za-z][A-Za-z0-9~/._+-]+')

    def __init__(self,
                 zone_id):
        super(ZoneId, self).__init__()
        self._zone_id = zone_id
        self._rules = None

    def get_rules(self):
        return self._rules

    @classmethod
    def of_Id(cls, zone_id, check_available):
        if len(zone_id) < 2 or zone_id[:3] == 'UTC' or zone_id[:3] == 'GMT' or cls.PATTERN.match(zone_id) is None:
            raise Exception
        return ZoneRegion(zone_id)

    def get_id(self):
        return self._zone_id





