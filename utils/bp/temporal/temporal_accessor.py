from abc import ABCMeta, abstractmethod


class TemporalAccessor(object):
    """
    Framework-level interface defining read-only access to a temporal object,
    such as a date, time, offset or some combination of these.
    This is the base interface type for date, time and offset objects.
    It is implemented by those classes that can provide information
    as {@link TemporalField fields} or {@link TemporalQuery queries}.
    Most date and time information can be represented as a number.
    These are modeled using {@code TemporalField} with the number held using
     a {@code long} to handle large values. Year, month and day-of-month are
     simple examples of fields, but they also include instant and offsets.
     See {@link ChronoField} for the standard set of fields.
     Two pieces of date/time information cannot be represented by numbers,
     the {@link Chronology chronology} and the {@link ZoneId time-zone}.
     These can be accessed via {@link #query(TemporalQuery) queries} using
     the static methods defined on {@link TemporalQueries}.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_supported(self, field):
        """
        Checks if the specified field is supported.
        This checks if the date-time can be queried for the specified field.
        If false, then calling the {@link #range(TemporalField) range} and {@link #get(TemporalField) get}
        methods will throw an exception.
        """
        pass

    @abstractmethod
    def range(self, field):
        """
        Gets the range of valid values for the specified field.
        @param field  the field to query the range for, not null
        @return the range of valid values for the field, not null
        @throws DateTimeException if the range for the field cannot be obtained
        """
        pass

    @abstractmethod
    def get(self, field):
        """
        Gets the value of the specified field as an {@code int}.
        @param field  the field to get, not null
        @return the value for the field, within the valid range of values
        """
        raise NotImplementedError()

    @abstractmethod
    def get_long(self, field):
        """
        Gets the value of the specified field as a {@code long}.
        @param field  the field to get, not null
        @return the value for the field
        """
        raise NotImplementedError()

    def query(self, query):
        """
        Queries this date-time.
        @param <R> the type of the result
        @param query  the query to invoke, not null
        """
        raise NotImplementedError()



