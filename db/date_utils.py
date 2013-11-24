import datetime as dt
from utils.bp.instant import Instant
from utils.bp.local_date import LocalDate
from utils.bp.local_date_time import LocalDateTime
from utils.bp.local_time import LocalTime


class DbDateUtils(object):

    MAX_SQL_DATE = LocalDate.of(9999 - 1900, 12, 31)
    MIN_SQL_DATE = LocalDate.of(1900, 1, 1)
    MAX_SQL_TIMESTAMP = dt.datetime(9999 - 1900, 12, 31, 23, 59, 59)
    EFFECTIVE_MAX_TIMESTAMP = MAX_SQL_TIMESTAMP
    MIN_SQL_TIMESTAMP = dt.datetime(1900, 1, 1)

    @classmethod
    def MAX_INSTANT(cls):
        return Instant.from_dt_datetime(cls.MAX_SQL_TIMESTAMP)

    @classmethod
    def MIN_INSTANT(cls):
        return Instant.from_dt_datetime(cls.MIN_SQL_TIMESTAMP)

    @classmethod
    def to_sql_timestamp(cls,
                         instant):

        d = instant.to_local_datetime(Instant.LOCAL_DEFAULT)
        d_main = d.strftime('%Y-%m-%d %H:%M:%S.%f')
        return d_main

    @classmethod
    def to_sql_timestamp_from_time(cls,
                                   time):
        return time.strftime('%H:%M:%S')

    @classmethod
    def from_sql_timestamp(cls,
                           timestamp):
        """
        returns instant
        """
        try:
            dt_value = dt.datetime.strptime(timestamp[:-3], '%Y-%m-%d %H:%M:%S.%f')
            instant_value = Instant.from_dt_datetime(dt_value)
            return instant_value
        except (TypeError, AttributeError), e:
            try:
                instant_value = Instant.from_dt_datetime(timestamp)
                return instant_value
            except (TypeError, AttributeError), e:
                raise Exception(e)

    @classmethod
    def from_sql_timestamp_null_far_future(cls,
                                           timestamp):
        try:
            instance_init = cls.from_sql_timestamp(timestamp)
        except OverflowError, e:
            instance_init = cls.from_sql_timestamp(cls.EFFECTIVE_MAX_TIMESTAMP)
        if instance_init >= cls.MAX_INSTANT():
            return None
        return instance_init

    @classmethod
    def from_sql_timestamp_null_far_past(cls, timestamp):
        instance_init = cls.from_sql_timestamp(timestamp)
        if instance_init <= cls.MIN_INSTANT():
            return None
        return instance_init

    @classmethod
    def to_sql_date_time(cls,
                         date_time):
        if isinstance(date_time, dt.datetime):
            return date_time.strftime('%Y-%m-%d')
        elif isinstance(date_time, LocalDate):
            return date_time.__str__()


    @classmethod
    def from_sql_date_time(cls,
                           sql_date_time):

        return cls.from_sql_timestamp(sql_date_time)

    @classmethod
    def to_sql_date(cls,
                    date_):
        if isinstance(date_, dt.date):
            return date_.strftime('%Y-%m-%d')
        elif isinstance(date_, LocalDate):
            return date_.__str__()

    @classmethod
    def to_sql_date_null_far_past(cls, date):
        if date is None:
            return cls.to_sql_date(cls.MIN_SQL_DATE)
        return cls.to_sql_date(date)

    @classmethod
    def to_sql_date_null_far_future(cls, date):
        if date is None:
            return cls.to_sql_date(cls.MAX_SQL_DATE)
        return cls.to_sql_date(date)

    @classmethod
    def from_sql_date(cls,
                      date_):
        try:
            init_dt = dt.datetime.strptime(date_,
                                           '%Y-%m-%d')
            return LocalDate.of(init_dt.year, init_dt.month, init_dt.day)
        except TypeError, ex:
            if isinstance(date_, dt.datetime):
                return LocalDate.of(date_.year, date_.month, date_.day)
            else:
                raise TypeError(ex)

    @classmethod
    def from_sql_date_null_far_future(cls, date):
        if date.__eq__(cls.MAX_SQL_DATE):
            return None
        return cls.from_sql_date(date)

    @classmethod
    def from_sql_date_null_far_past(cls, date):
        if date.__eq__(cls.MIN_SQL_DATE):
            return None
        return cls.from_sql_date(date)

    @classmethod
    def from_sql_date_allow_null(cls, date):
        return cls.from_sql_date(date) if date is not None else None

    @classmethod
    def from_sql_date_time(cls,
                           date_time):
        if isinstance(date_time, dt.datetime):
            date = LocalDate.of(date_time.year, date_time.month, date_time.day)
            time = LocalTime.of(date_time.hour, date_time.minute, date_time.second, date_time.microsecond*1000)
            return LocalDateTime.of(date, time)
        else:
            raise TypeError('Not a date time')

    @classmethod
    def from_sql_date_time_null_far_future(cls, date_time):
        if cls.to_sql_date(date_time).__eq__(cls.MAX_SQL_DATE):
            return None
        return cls.from_sql_date_time(date_time)

    @classmethod
    def from_sql_date_time_null_far_past(cls, date_time):
        if cls.to_sql_date(date_time).__eq__(cls.MIN_SQL_DATE):
            return None
        return cls.from_sql_date_time(date_time)

    @classmethod
    def from_sql_date_time_allow_null(cls, date_time):
        return cls.from_sql_date_time(date_time) if date_time is not None else None




