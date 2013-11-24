__author__ = 'Tyler'
import numpy as np
from utils.bp.temporal.temporal_queries import TemporalQueries

class ZoneOffset(object):
    def __init__(self, total_seconds):
        self.total_seconds = total_seconds
        self.id = ZoneOffset.build_id(total_seconds)

    SECONDS_CACHE = dict()
    ID_CACHE = dict()
    ID_CACHE = dict()
    SECONDS_PER_HOUR = 60 * 60
    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HOUR = 60
    MAX_SECONDS = 18 * SECONDS_PER_HOUR

    @classmethod
    def of(cls, offset_id):
        offset = cls.ID_CACHE.get(offset_id)
        if offset is not None:
            return offset
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


