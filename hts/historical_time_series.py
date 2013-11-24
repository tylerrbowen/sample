from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from ids.unique_identifiable import UniqueIdentifiable


class HistoricalTimeSeries(UniqueIdentifiable):
    """
    A historical time-series providing a value for a series of dates.
    This provides a time-series on a daily basis that is associated with a unique identifier.
    This interface is read-only.
    Implementations may be mutable.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_unique_id(self):
        """
        Gets the unique identifier of the historical time-series.
        This specifies a single version-correction of the time-series.
        @return the unique identifier for this series, not null within the engine
        """
        pass

    @abstractmethod
    def get_time_series(self):
        """
        Gets the time-series data.
        @return: LocalDateDoubleTimeSeries: the series, not null
        """
        pass
