

from hts.historical_time_series import HistoricalTimeSeries
from ids.unique_identifiable import UniqueIdentifiable
from ids.mutable_unique_identifiable import MutableUniqueIdentifiable


class ManageableHistoricalTimeSeries(HistoricalTimeSeries, UniqueIdentifiable, MutableUniqueIdentifiable):
    """
    A time-series as stored in a master.
    The time-series is stored separately from the information describing it.
    See {@link ManageableHistoricalTimeSeriesInfo}.
    This class is mutable and not thread-safe.
    """
    def __init__(self):
        """
        _unique_id: UniqueId: The historical time-series unique identifier.
        _version_instant: Instant: The instant that this version was created.
        _correction_instant: Instant: The instant that this version was corrected at.
        _time_series: LocalDateDoubleTimeSeries: The time-series.
        """
        self._unique_id = None
        self._version_instant = None
        self._correction_instant = None
        self._time_series = None

    def get_unique_id(self):
        return self._unique_id

    def set_unique_id(self, unique_id):
        self._unique_id = unique_id

    def get_time_series(self):
        return self._time_series

    def set_time_series(self, time_series):
        self._time_series = time_series

    def get_correction_instant(self):
        return self._correction_instant

    def set_correction_instant(self, correction_instant):
        self._correction_instant = correction_instant

    def get_version_instant(self):
        return self._version_instant

    def set_version_instant(self, version_instant):
        self._version_instant = version_instant

    def __eq__(self, other):
        if self is other:
            return True
        if other is not None and isinstance(other, ManageableHistoricalTimeSeries):
            return self.get_unique_id() == other.get_unique_id() and \
                self.get_correction_instant() == other.get_correction_instant() and \
                self.get_version_instant() == other.get_version_instant() and \
                self.get_time_series() == other.get_time_series()
        return False

    def __hash__(self):
        h = self.__class__.__name__.__hash__()
        h += h * 31 + self.get_unique_id().__hash__()
        h += h * 31 + self.get_version_instant().__hash__()
        h += h * 31 + self.get_correction_instant().__hash__()
        h += h * 31 + self.get_time_series().__hash__()
        return h



