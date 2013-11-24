
from abc import ABCMeta
from utils.bp.temporal.temporal_accessor import TemporalAccessor
from utils.bp.temporal.chrono_field import ChronoFieldItem
from utils.bp.temporal.temporal_queries import TemporalQueries


class DefaultInterfaceTemporalAccessor(TemporalAccessor):
    __metaclass__ = ABCMeta

    def range(self, field):
        if isinstance(field, ChronoFieldItem):
            if self.is_supported(field):
                return field.range()
            raise TypeError('Unsupported Field')
        return field.range_refined_by(self)

    def get(self, field):
        return self.range(field)

    def query(self, query):
        if query == TemporalQueries.zone_id() or query ==  TemporalQueries.chronology() or query == TemporalQueries.precision():
            return None
        return query.query_from(self)