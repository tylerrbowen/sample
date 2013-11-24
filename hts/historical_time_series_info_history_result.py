

from abstracts.abstract_history_result import AbstractHistoryResult


class HistoricalTimeSeriesInfoHistoryResult(AbstractHistoryResult):
    """
    Result from searching historical time-series information.

    """
    def __init__(self,
                 coll=None):
        """
        @param coll  the collection of documents to add, not null
        """
        super(HistoricalTimeSeriesInfoHistoryResult, self).__init__(coll)

    def get_info_list(self):
        """
        Gets the returned series information from within the documents.
        """
        result = []
        if self.get_documents() is not None:
            for doc in self.get_documents():
                result.append(doc.get_info())
        return result

    def get_first_info(self):
        """
        Gets the first series information, or null if no documents.
        """
        return self.get_first_document().get_info() if len(self.get_documents()) > 0 else None

    def get_single_info(self):
        """
        Gets the single result expected from a query.
        """
        if len(self.get_documents()) != 0:
            raise RuntimeError('Expecting zero or single match, not many')
        else:
            return self.get_documents()[0].get_info()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return super(self.__class__, self).__eq__(other)
        return False

    def __hash__(self):
        h = 7
        return h ^ super(self.__class__, self).__hash__()

