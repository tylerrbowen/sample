from utils.paging import PagingRequest
from ids.version_correction import VersionCorrection
from utils.id_utils import IdUtils


class AbstractSearchRequest(object):

    def __init__(self):
        self._paging_request = PagingRequest.ALL()
        self._version_correction = VersionCorrection.LATEST()

    def set_version_correction(self, version_correction):
        self._version_correction = version_correction

    def matches(self, document):
        return self.get_version_correction() is None or \
            IdUtils.is_version_correction(vc=document.get_version_correction(),
                                          version_from=document.get_version_from_instant(),
                                          version_to=document.get_version_to_instant(),
                                          correction_from=document.get_correction_from_instant(),
                                          correction_to=document.get_correction_to_instant())

    def __eq__(self, other):
        if not isinstance(other, AbstractSearchRequest):
            return False
        return self.get_paging_request() == other.get_paging_request() and \
            self.get_version_correction() == other.get_version_correction()

    def get_paging_request(self):
        return self._paging_request

    def get_version_correction(self):
        return self._version_correction

    def set_paging_request(self, paging_request):
        self._paging_request = paging_request
