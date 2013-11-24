from utils.bp.temporal.temporal_queries import TemporalQuery, TemporalQueries

class _query_region_only(TemporalQuery):

    def query_from(self, temporal):
        zone = temporal.query(TemporalQueries.zone_id())
        return  zone if zone is not None and not isinstance(zone, ZoneOffset) else None




class DateTimeFormatterBuilder(object):

    def __init__(self,
                 parent=None,
                 optional=None):
        self._active = self
        if parent is not None:
            assert optional is not None
            self._parent = parent
            self._optional = optional
        else:
            self._parent = None
            self._optional = False
        self._printer_parsers = []

        self._pad_next_width = None
        self._pad_next_char = None
        self._value_parser_index = -1

    def parse_case_sensitive(self):
        self.append_internal()
