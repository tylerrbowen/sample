from abc import ABCMeta, abstractmethod


class TemporalQuery(object):
    """
    Strategy for querying a temporal object.
    Queries are a key tool for extracting information from temporal objects.
    They exist to externalize the process of querying, permitting different
    approaches, as per the strategy design pattern.
    Examples might be a query that checks if the date is the day before February 29th
    in a leap year, or calculates the number of days to your next birthday.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def query_from(self, temporal):
        """
        Queries the specified temporal object.
        This queries the specified temporal object to return an object using the logic
        encapsulated in the implementing class.
        """
        raise NotImplementedError()


class TemporalQueries(object):
    """
    Common implementations of {@code TemporalQuery}.
    This class provides common implementations of {@link TemporalQuery}.
    These queries are primarily used as optimizations, allowing the internals
    of other objects to be extracted effectively. Note that application code
    can also use the {@code from(TemporalAccessor)} method on most temporal
    objects as a method reference matching the query interface, such as
    {@code LocalDate::from} and {@code ZoneId::from}.
    """

    @classmethod
    def ZONE_ID(cls):
        return _zone_id_def()

    @classmethod
    def CHRONO(cls):
        return _chrono_def()

    @classmethod
    def PRECISION(cls):
        return _chrono_def()

    @classmethod
    def ZONE(cls):
        return _zone_def()

    @classmethod
    def OFFSET(cls):
        offset_inst = _offset_def()
        return offset_inst

    @classmethod
    def LOCAL_DATE(cls):
        local_date_inst = _local_date_def()
        return local_date_inst

    @classmethod
    def LOCAL_TIME(cls):
        local_time_inst = _local_time_def()
        return local_time_inst

    @classmethod
    def zone_id(cls):
        return cls.ZONE_ID()

    @classmethod
    def chronology(cls):
        return cls.CHRONO()

    @classmethod
    def precision(cls):
        return cls.PRECISION()

    @classmethod
    def zone(cls):
        return cls.ZONE()

    @classmethod
    def offset(cls):
        return cls.OFFSET()

    @classmethod
    def local_date(cls):
        return cls.LOCAL_DATE()

    @classmethod
    def local_time(cls):
        return cls.LOCAL_TIME()

    @classmethod
    def zone_id(cls):
        return cls.ZONE_ID()

    @classmethod
    def zone_id(cls):
        return cls.ZONE_ID()


class _zone_id_def(TemporalQuery):
    def __init__(self):
        super(_zone_id_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)

class _precision_def(TemporalQuery):
    def __init__(self):
        super(_precision_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)

class _chrono_def(TemporalQuery):
    def __init__(self):
        super(_chrono_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)


class _zone_def(TemporalQuery):
    def __init__(self):
        super(_zone_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)

class _offset_def(TemporalQuery):
    def __init__(self):
        super(_offset_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)

class _local_date_def(TemporalQuery):
    def __init__(self):
        super(_local_date_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)


class _local_time_def(TemporalQuery):
    def __init__(self):
        super(_local_time_def, self).__init__()

    def query_from(self, temporal):
        return temporal.query(self)




