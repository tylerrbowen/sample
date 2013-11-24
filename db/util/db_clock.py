import datetime
from utils.shared_clock import SharedClock
from db.date_utils import DbDateUtils
from utils.bp.clock import Clock, Instant
import delorean
import calendar
import time
from db.db_connector import DbConnector


class DbClock(Clock):

    def __init__(self,
                 db_connector):
        self._connector = db_connector
        self._precision = db_connector.get_dialect().get_timestamp_precision()
        self._zone = 'UTC'
        now = calendar.timegm(time.gmtime())*1000000000
        self._now_nano_time = now
        self._now_instant = None

    def instant(self):
        now_nanos = calendar.timegm(time.gmtime())*1000000000
        if now_nanos - (self._now_nano_time + 1000000000) > 0 or self._now_instant is None:
            self._now_instant = DbDateUtils.from_sql_timestamp(self._connector.now_db()).truncated_to(self._precision)
            self._now_nano_time = calendar.timegm(time.gmtime())*1000000000
            return self._now_instant
        now_nanos = calendar.timegm(time.gmtime())*1000000000
        interpolate = max(now_nanos - self._now_nano_time, 0)
        precision_nano = self._precision.get_duration().get_nano()
        interpolate = (interpolate / precision_nano) * precision_nano
        result = self._now_instant.plus_nanos(interpolate)
        return result

    def __str__(self):
        return 'DbClock'

    def __eq__(self, other):
        return False

    def __hash__(self):
        return 'UTC'.__hash__() + 1









