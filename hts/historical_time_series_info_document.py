
from abstracts.abstract_document import AbstractDocument
from hts.manageable_historical_time_series_info import ManageableHistoricalTimeSeriesInfo


class HistoricalTimeSeriesInfoDocument(AbstractDocument):
    """
    A document used to pass into and out of the historical time-series master.
    This document stores information about the time-series, not the time-series itself.
    This class is mutable and not thread-safe.
    """
    def __init__(self,
                  info=None):
        self._info = None
        super(HistoricalTimeSeriesInfoDocument, self).__init__()
        if info is None:
            info = ManageableHistoricalTimeSeriesInfo()
        self.set_info(info)

    def get_unique_id(self):
        return self.get_info().get_unique_id()

    def set_unique_id(self, unique_id):
        self.get_info().set_unique_id(unique_id)

    def get_value(self):
        return self.get_info()

    def get_info(self):
        return self._info

    def set_info(self, info):
        self._info = info

    def __eq__(self, other):
        if self is other:
            return True
        if other is not None and isinstance(other, HistoricalTimeSeriesInfoDocument):
            return self.get_info().__eq__(other.get_info()) and \
                self.get_unique_id().__eq__(other.get_unique_id())
        return False

    def __hash__(self):
        h = 7
        h += h * 31 + self.get_info().__hash__()
        h += h * 31 + self.get_unique_id().__hash__()
        h ^= super(HistoricalTimeSeriesInfoDocument, self).__hash__()
        return h





