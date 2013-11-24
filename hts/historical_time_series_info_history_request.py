
from abstracts.abstract_history_request import AbstractHistoryRequest


class HistoricalTimeSeriesInfoHistoryRequest(AbstractHistoryRequest):
    """
    Request for the history of a time-series information.
    A full time-series master implements historical storage of data.
    History can be stored in two dimensions and this request provides searching.
    The first historic dimension is the classic series of versions.
    Each new version is stored in such a manor that previous versions can be accessed.
    The second historic dimension is corrections.
    A correction occurs when it is realized that the original data stored was incorrect.
    A simple exchange master might simply replace the original version with the corrected value.
    A full implementation will store the correction in such a manner that it is still possible
    to obtain the value before the correction was made.

    """
    def __init__(self,
                 object_id=None,
                 version_instant=None,
                 corrected_to_instant=None):
        super(HistoricalTimeSeriesInfoHistoryRequest, self).__init__(object_id,
                                                                     version_instant,
                                                                     corrected_to_instant)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, HistoricalTimeSeriesInfoHistoryRequest):
            return super(HistoricalTimeSeriesInfoHistoryRequest, self).__eq__(other)

    def __hash__(self):
        h = 7
        h ^= super(HistoricalTimeSeriesInfoHistoryRequest, self).__hash__()
        return h


