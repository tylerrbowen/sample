

from abstracts.abstract_search_result import AbstractSearchResult


class HistoricalTimeSeriesInfoSearchResult(AbstractSearchResult):

    def __init__(self,
                 coll=None,
                 version_correction=None):
        super(HistoricalTimeSeriesInfoSearchResult, self).__init__(coll)
        if version_correction is not None:
            self.set_version_correction(version_correction)


    def get_info_list(self):
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

