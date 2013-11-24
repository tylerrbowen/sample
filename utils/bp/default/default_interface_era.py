

from default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from abc import ABCMeta, abstractmethod
from utils.bp.chrono.era import Era
from utils.bp.date_time_exception import DateTimeException
from utils.bp.temporal.chrono_field import ChronoFieldItem, ChronoField
from utils.bp.temporal.temporal_queries import TemporalQueries
from utils.bp.format.date_time_formatter_builder import DateTimeFormatterBuilder


class DefaultInterfaceEra(DefaultInterfaceTemporalAccessor, Era):
    __metaclass__ = ABCMeta

    def date(self, year_of_era, month, day):
        return self.get_chronology().date(self, year_of_era, month, day)

    def date_year_day(self, year_of_era, day_of_year):
        return self.get_chronology().date_year_day(self, year_of_era, day_of_year)

    def is_supported(self, field):
        if isinstance(field, ChronoFieldItem):
            return  field == ChronoField.ERA
        return  field is not None and field.is_supported_by(self)

    def get(self, field):
        if field == ChronoField.ERA:
            return self.get_value()
        elif isinstance(field, ChronoFieldItem):
            raise DateTimeException('Unsupported field: ' + field.get_name())
        return field.get_from(self)

    def adjust_into(self, temporal):
        return temporal.with_field(ChronoField.ERA, self.get_value())

    def query(self, query):
        if query == TemporalQueries.chronology():
            return self.get_chronology()
        return super(DefaultInterfaceEra, self).query(query)

    def get_display_name(self, style, locale):
        return DateTimeFormatterBuilder().append_text(ChronoField.ERA, style).to_formatter(locale).format(self)



