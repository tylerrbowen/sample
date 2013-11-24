

class HistoricalTimeSeriesGetFilter(object):
    """
    Request for getting the data points of a time-series.
    This allows a subset of the total time-series to be returned, effectively
    acting as a filter.
    """

    def __init__(self):
        self._earliest_date = None
        self._latest_date = None
        self._max_points = None

    @classmethod
    def of_all(cls):
        return HistoricalTimeSeriesGetFilter()

    @classmethod
    def of_latest_point(cls, earliest_date=None, latest_date=None):
        if earliest_date is not None and latest_date is not None:
            request = HistoricalTimeSeriesGetFilter.of_range(earliest_date, latest_date)
        else:
            request = HistoricalTimeSeriesGetFilter()
        request.set_max_points(-1)
        return request

    @classmethod
    def of_earliest_point(cls, earliest_date=None, latest_date=None):
        if earliest_date is not None and latest_date is not None:
            request = HistoricalTimeSeriesGetFilter.of_range(earliest_date, latest_date)
        else:
            request = HistoricalTimeSeriesGetFilter()
        request.set_max_points(1)
        return request

    @classmethod
    def of_range(cls, earliest_date, latest_date):
        request = HistoricalTimeSeriesGetFilter()
        request.set_earliest_date(earliest_date)
        request.set_latest_date(latest_date)
        return request

    def get_earliest_date(self):
        return self._earliest_date

    def set_earliest_date(self, earliest_date):
        self._earliest_date = earliest_date

    def get_latest_date(self):
        return self._latest_date

    def set_latest_date(self, latest_date):
        self._latest_date = latest_date

    def get_max_points(self):
        return self._max_points

    def set_max_points(self, max_points):
        self._max_points = max_points





