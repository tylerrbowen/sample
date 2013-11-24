
from ids.unique_identifiable import UniqueIdentifiable
from abc import ABCMeta, abstractmethod


class HistoricalTimeSeriesInfo(UniqueIdentifiable):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_external_id_bundle(self):
        """

        """
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_data_field(self):
        pass

    @abstractmethod
    def get_data_source(self):
        pass

    @abstractmethod
    def get_data_provider(self):
        pass

    @abstractmethod
    def get_observation_time(self):
        pass

    @abstractmethod
    def get_time_series_object_id(self):
        pass
