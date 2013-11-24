__author__ = 'AH0137307'
from abstract_document_result import AbstractDocumentsResult


class AbstractHistoryResult(AbstractDocumentsResult):
    def __init__(self,
                 collection_results=[]):
        super(AbstractHistoryResult, self).__init__(collection_results)


    def get_first_document(self):
        return self.get_documents()[0] if len(self.get_documents()) > 0 else None

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, AbstractHistoryResult):
            return super(AbstractHistoryResult, self).__eq__(other)
        return False

    def __hash__(self):
        h = 7
        return h ^ super(AbstractHistoryResult, self).__hash__()




