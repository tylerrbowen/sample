

from historical_time_series_info import HistoricalTimeSeriesInfo
from ids.mutable_unique_identifiable import MutableUniqueIdentifiable


class ManageableHistoricalTimeSeriesInfo(HistoricalTimeSeriesInfo, MutableUniqueIdentifiable):
    """
    The information about a historical time-series.
    This is used to hold the information about a time-series in the master. The actual time-series is held separately.
    This class is mutable and not thread-safe.
    """
    def __init__(self):
        self._unique_id = None
        self._external_id_bundle = None
        self._name = None
        self._data_field = None
        self._data_provider = None
        self._data_source = None
        self._data_provider = None
        self._observation_time = None
        self._time_series_object_id = None

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ManageableHistoricalTimeSeriesInfo):
            return self.get_unique_id() == other.get_unique_id() and \
                self.get_name() == other.get_name() and \
                self.get_data_field() == other.get_data_field() and \
                self.get_data_source() == other.get_data_source() and \
                self.get_data_provider() == other.get_data_provider() and \
                self.get_observation_time() == other.get_observation_time() and \
                self.get_time_series_object_id() == other.get_time_series_object_id()
        return False

    def __hash__(self):
        h = self.__class__.__name__.__hash__()
        h += h * 31 + self.get_unique_id().__hash__()
        h += h * 31 + self.get_name().__hash__()
        h += h * 31 + self.get_data_field().__hash__()
        h += h * 31 + self.get_data_source().__hash__()
        h += h * 31 + self.get_data_provider().__hash__()
        h += h * 31 + self.get_observation_time().__hash__()
        h += h * 31 + self.get_time_series_object_id().__hash__()
        return h

    def get_unique_id(self):
        return self._unique_id

    def set_unique_id(self, unique_id):
        self._unique_id = unique_id

    def get_external_id_bundle(self):
        return self._external_id_bundle

    def set_external_id_bundle(self, external_id_bundle):
        self._external_id_bundle = external_id_bundle

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_data_field(self):
        return self._data_field

    def set_data_field(self, data_field):
        self._data_field = data_field

    def get_data_provider(self):
        return self._data_provider

    def set_data_provider(self, data_provider):
        self._data_provider = data_provider

    def get_data_source(self):
        return self._data_source

    def set_data_source(self, data_source):
        self._data_source = data_source

    def get_observation_time(self):
        return self._observation_time

    def set_observation_time(self, observation_time):
        self._observation_time = observation_time

    def get_time_series_object_id(self):
        return self._time_series_object_id

    def set_time_series_object_id(self, time_series_object_id):
        self._time_series_object_id = time_series_object_id





