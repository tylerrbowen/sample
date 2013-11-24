__author__ = 'AH0137307'
from utils.paging import PagingRequest


class AbstractHistoryRequest(object):
    def __init__(self,
                 object_id,
                 version_instant=None,
                 corrected_to_instant=None):
        self._paging_request = PagingRequest.ALL()
        self._object_id = object_id
        self._versions_from_instant = version_instant
        self._versions_to_instant = version_instant
        self._corrections_from_instant = corrected_to_instant
        self._corrections_to_instant = corrected_to_instant

    def set_paging_request(self, paging_request):
        self._paging_request = paging_request

    def get_paging_request(self):
        return self._paging_request

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_object_id(self):
        return self._object_id

    def get_versions_from_instant(self):
        return self._versions_from_instant

    def set_versions_from_instant(self, versions_from_instant):
        self._versions_from_instant = versions_from_instant

    def get_versions_to_instant(self):
        return self._versions_to_instant

    def set_versions_to_instant(self, versions_to_instant):
        self._versions_to_instant = versions_to_instant

    def get_corrections_from_instant(self):
        return self._corrections_from_instant

    def set_corrections_to_instant(self, corrections_to_instant):
        self._corrections_to_instant = corrections_to_instant

    def set_corrections_from_instant(self, corrections_from_instant):
        self._corrections_from_instant = corrections_from_instant

    def get_corrections_to_instant(self):
        return self._corrections_to_instant

    def set_corrections_to_instant(self, corrections_to_instant):
        self._corrections_to_instant = corrections_to_instant

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, AbstractHistoryRequest):
            return self.get_paging_request() == other.get_paging_request() and \
                self.get_object_id() == other.get_object_id() and \
                self.get_versions_from_instant() == other.get_versions_from_instant() and \
                self.get_versions_to_instant() == other.get_versions_to_instant() and \
                self.get_corrections_to_instant() == other.get_corrections_to_instant() and \
                self.get_corrections_from_instant() == other.get_corrections_from_instant()
        return False

    def __hash__(self):
        h = self.__class__.__name__.__hash__()
        h += h * 31 + self.get_paging_request().__hash__()
        h += h * 31 + self.get_object_id().__hash__()
        h += h * 31 + self.get_versions_from_instant().__hash__()
        h += h * 31 + self.get_versions_to_instant().__hash__()
        h += h * 31 + self.get_corrections_to_instant().__hash__()
        h += h * 31 + self.get_corrections_from_instant().__hash__()
        return h




class AbstractHistoryRequestPreviousDocument(AbstractHistoryRequest):
    def __init__(self,
                 caller,
                 object_id=None,
                 version_instant=None,
                 corrected_to_instant=None):
        super(AbstractHistoryRequestPreviousDocument, self).__init__(object_id=object_id,
                                                                     version_instant=version_instant,
                                                                     corrected_to_instant=corrected_to_instant)
        self._caller = caller
        self._call_object_id = object_id
        self._call_version_instant = version_instant
        self._call_corrected_to_instant = corrected_to_instant

    def get_corrections_from_instant(self):
        return self._caller.now()

    def get_object_id(self):
        return self._call_object_id

    def get_paging_request(self):
        return PagingRequest.ONE()

    def get_versions_from_instant(self):
        return self._call_version_instant.minus_millis(1)

    def get_versions_to_instant(self):
        return self._call_version_instant.minus_millis(1)


class AbstractHistoryRequestAllCurrent(AbstractHistoryRequest):
    def __init__(self,
                 caller,
                 object_id=None,
                 version_instant=None):
        super(AbstractHistoryRequestAllCurrent, self).__init__(object_id=None,
                                                               version_instant=None)
        self._caller = caller
        self._call_object_id = object_id
        self._call_version_instant = version_instant

    def get_corrections_from_instant(self):
        return self._call_version_instant

    def get_corrections_to_instant(self):
        return self._call_version_instant

    def get_object_id(self):
        return self._call_object_id

    def get_paging_request(self):
        return PagingRequest.ALL()

    def get_versions_from_instant(self):
        return None

    def get_versions_to_instant(self):
        return None


class AbstractHistoryRequestCurrentInRange(AbstractHistoryRequest):
    def __init__(self,
                 caller,
                 object_id=None,
                 now=None,
                 instant_from=None,
                 instant_to=None):
        super(AbstractHistoryRequestCurrentInRange, self).__init__(object_id=object_id)
        self._caller = caller
        self._call_object_id = object_id
        self._call_now = now
        self._call_from = instant_from
        self._call_to = instant_to

    def get_corrections_from_instant(self):
        return self._call_now

    def get_corrections_to_instant(self):
        return self._call_now

    def get_object_id(self):
        return self._call_object_id

    def get_paging_request(self):
        return PagingRequest.ALL()

    def get_versions_from_instant(self):
        return self._call_from

    def get_versions_to_instant(self):
        return self._call_to