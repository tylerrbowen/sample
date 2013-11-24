import datetime


class LocalTime(object):

    def __init__(self,
                 hour,
                 minute,
                 second,
                 nano_of_second):
        self._hour = hour
        self._minute = minute
        self._second = second
        self._nano = nano_of_second

    HOURS_PER_DAY = 24
    MINUTES_PER_HOUR = 60
    MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
    SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY;
    MILLIS_PER_DAY = SECONDS_PER_DAY * 1000L;
    MICROS_PER_DAY = SECONDS_PER_DAY * 1000000L;
    NANOS_PER_SECOND = 1000000000L;
    NANOS_PER_MINUTE = NANOS_PER_SECOND * SECONDS_PER_MINUTE;
    NANOS_PER_HOUR = NANOS_PER_MINUTE * MINUTES_PER_HOUR;
    NANOS_PER_DAY = NANOS_PER_HOUR * HOURS_PER_DAY;

    MIN = None
    MAX = None
    MIDNIGHT = None
    MIDNIGHT = None
    NOON = None

    @classmethod
    def parse(cls, text, formatter=None):
        datetimedate = datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        return LocalTime(datetimedate.hour, datetimedate.minute, datetimedate.second, datetimedate.microsecond*1000)

    def __init__(self,
                 hour,
                 minute,
                 second,
                 nano_of_second):
        self._hour = hour
        self._minute = minute
        self._second = second
        self._nano_of_second = nano_of_second

    @classmethod
    def of(cls, hour, minute, second, nano_of_second):
        return LocalTime(hour, minute, second, nano_of_second)

    @classmethod
    def of_second_of_day(cls, second_of_day, nano_of_second=0):
        hours = int(second_of_day / cls.SECONDS_PER_HOUR)
        second_of_day -= hours * cls.SECONDS_PER_HOUR
        minutes = int(second_of_day / cls.SECONDS_PER_MINUTE)
        second_of_day -= minutes * cls.SECONDS_PER_MINUTE
        return LocalTime(hours, minutes, second_of_day, nano_of_second)


    def get_hour(self):
        return self._hour

    def get_minute(self):
        return self._minute

    def get_second(self):
        return self._second

    def get_nano(self):
        return self._nano

    def __str__(self):
        h = '0' + self.get_hour().__str__() if self.get_hour() < 10 else self.get_hour().__str__()
        m = '0' + self.get_minute().__str__() if self.get_minute() < 10 else self.get_minute().__str__()
        s = '0' + self.get_second().__str__() if self.get_second() < 10 else self.get_second().__str__()
        return h + m + s


def minus_millis(t, minus):
    delta = datetime.timedelta(0, 0, 1000*minus)
    return t - delta