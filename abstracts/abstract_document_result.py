__author__ = 'AH0137307'
from utils.paging import Paging


class AbstractDocumentsResult(object):
    def __init__(self,
                 collection_results=None):
        if not collection_results:
            collection_results = []
        self._paging = Paging.ofAll(collection_results)
        self._documents = collection_results

    def get_first_document(self):
        if len(self._documents) > 0:
            return self._documents[0]
        else:
            return None

    def get_documents(self):
        return self._documents

    def get_paging(self):
        return self._paging

    def set_paging(self, paging):
        self._paging = paging

    def set_documents(self, documents=None):
        if not documents:
            documents = []
        self._documents = documents

    def __eq__(self, other):
        if not isinstance(other, AbstractDocumentsResult):
            return False
        return self.get_documents() == other.get_documents() and \
            self.get_paging() == other.get_paging()

    def __hash__(self):
        h = self.__class__.__name__.__hash__()
        h += h * 31 + self.get_paging().__hash__()
        for doc in self._documents:
            h += h * 31 + doc.__hash__()
        return h








