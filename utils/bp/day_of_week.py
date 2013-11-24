
from utils.new_enum import EnumeratedType, Item
from temporal.temporal_accessor import TemporalAccessor
from temporal.temporal_adjuster import TemporalAdjuster
from date_time_exception import DateTimeException
from temporal.chrono_field import ChronoField


class DayOfWeek(EnumeratedType): #, TemporalAccessor, TemporalAdjuster):
    """
    A day-of-week, such as 'Tuesday'.
    {@code DayOfWeek} is an enum representing the 7 days of the week -
    Monday, Tuesday, Wednesday, Thursday, Friday, Saturday and Sunday.
    In addition to the textual enum name, each day-of-week has an {@code int} value.
    The {@code int} value follows the ISO-8601 standard, from 1 (Monday) to 7 (Sunday).
     It is recommended that applications use the enum rather than the {@code int} value
     to ensure code clarity.
    """
    MONDAY = Item('MONDAY')
    TUESDAY = Item('TUESDAY')
    WEDNESDAY = Item('WEDNESDAY')
    THURSDAY = Item('THURSDAY')
    FRIDAY = Item('FRIDAY')
    SATURDAY = Item('SATURDAY')
    SUNDAY = Item('SUNDAY')

    ENUMS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]

    @classmethod
    def of(cls, day_of_week):
        """
        Obtains an instance of {@code DayOfWeek} from an {@code int} value.
        {@code DayOfWeek} is an enum representing the 7 days of the week.
        This factory allows the enum to be obtained from the {@code int} value.
        The {@code int} value follows the ISO-8601 standard, from 1 (Monday) to 7 (Sunday).
        @param dayOfWeek  the day-of-week to represent, from 1 (Monday) to 7 (Sunday)
        @return the day-of-week singleton, not null
        @throws DateTimeException if the day-of-week is invalid
        """
        if day_of_week < 1 or day_of_week > 7:
            raise DateTimeException('Invalid value for DayofWeek: ' + day_of_week.__str__())
        return cls.ENUMS[day_of_week-1]

    @classmethod
    def from_temporal(cls, temporal):
        """
        Obtains an instance of {@code DayOfWeek} from a temporal object.
        A {@code TemporalAccessor} represents some form of date and time information.
        This factory converts the arbitrary temporal object to an instance of {@code DayOfWeek}.
        The conversion extracts the {@link ChronoField#DAY_OF_WEEK DAY_OF_WEEK} field.
        This method matches the signature of the functional interface {@link TemporalQuery}
        allowing it to be used as a query via method reference, {@code DayOfWeek::from}.
        @param temporal  the temporal object to convert, not null
        @return the day-of-week, not null

        """
        if isinstance(temporal, DayOfWeek):
            return temporal
        return cls.of(temporal.get(ChronoField.DAY_OF_WEEK.chrono_field))

    def get_value(self):
        return self.sort_index + 1

    def get_display_name(self, style, locale):
        return DateTimeFormatterBuilder().append_text(ChronoField.DAY_OF_WEEK.chrono_field, style).to_formatter(locale).format(self)

    def is_supported(self, field):
        if isinstance(field, ChronoField):
            return field == ChronoField.DAY_OF_WEEK.chrono_field
        return field is not None and field.is_supported_by(self)

    def range(self, field):
        if field == ChronoField.DAY_OF_WEEK.chrono_field:
            return field.range()
        elif isinstance(field, ChronoField):
            raise DateTimeException('Unsupported Field: ' + field.get_name())
        return field.range_refined_by(self)

    def get(self, field):
        if field == ChronoField.DAY_OF_WEEK.chrono_field:
            return self.get_value()
        return self.range(field).check_valid_int_value(self.get_long(field), field)

    def get_long(self, field):
        if field == ChronoField.DAY_OF_WEEK.chrono_field:
            return self.get_value()
        elif isinstance(field, ChronoField):
            raise DateTimeException('Unsupported Field: ' + field.get_name())
        return field.get_from(self)

    def plus(self, days):
        amount = int(days % 7)
        return self.ENUMS[(self.sort_index + (amount + 7)) % 7]

    def minus(self, days):
        return self.plus(-(days % 7))

    def query(self, query):
        if query == TemporalQueries.precision():
            return ChronoField.D


