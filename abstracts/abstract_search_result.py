
from abstract_document_result import AbstractDocumentsResult
from ids.version_correction import VersionCorrection


class AbstractSearchResult(AbstractDocumentsResult):
    def __init__(self,
                 documents=None):
        if not documents:
            documents=[]
        super(AbstractSearchResult, self).__init__(documents)

        self._version_correction = VersionCorrection.LATEST()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.get_version_correction() == other.get_version_correction() and \
            super(self.__class__, self).__eq__(other)

    def __hash__(self):
        h = 7
        h += h * 31 + self.get_version_correction().__hash__()
        return h ^ super(AbstractSearchResult, self).__hash__()

    def get_version_correction(self):
        return self._version_correction

    def set_version_correction(self, version_correction):
        self._version_correction = version_correction
