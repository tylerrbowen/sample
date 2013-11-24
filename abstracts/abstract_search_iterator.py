__author__ = 'AH0137307'
import numpy as np
from utils.paging import PagingRequest


class AbstractSearchIterator(object):
    def __init__(self,
                 master,
                 request):
        self._master = master
        self._request = request
        self._current_batch = None
        self._current_batch_index = None
        self._current = None
        self._overall_index = None

    def has_next(self):
        if self._current_batch is None or self._current_batch >= len(self._current_batch.get_documents()):
            self.do_fetch()
        return not self._current_batch and self._current_batch_index < len(self._current_batch.get_documents())

    def next(self):
        if not self.has_next():
            raise Exception
        return self.do_next()

    def remove(self):
        if not self._current:
            raise Exception

    def next_index(self):
        return self._overall_index

    def do_fetch(self):
        try:
            self._request.set_paging_request(PagingRequest.ofIndex(self._overall_index, 20))
            self._current_batch = self.do_search(self._request)
        except Exception:
            pass
        self._request.set_version_correction(self._current_batch.get_version_correction())
        if self._current_batch.get_paging().get_first_item() < self._overall_index:
            self._current_batch_index = self._overall_index - self._current_batch.get_paging().get_first_item()
        else:
            self._current_batch_index = 0

    def do_search(self):
        return

    def do_fetch_one(self, ex):
        max_failures = 5
        if self._current_batch:
            max_failures = self._current_batch.get_paging().get_total_items() - self._overall_index
            max_failures = np.min(max_failures, 20)
        while max_failures > 0:
            try:
                self._request.set_paging_request(PagingRequest.ofIndex(self._overall_index, 1))
                self._current_batch = self.do_search(self._request)
                return
            except Exception:
                self._overall_index += 1
                max_failures -= 1
        raise Exception

    def do_next(self):
        self._current = self._current_batch.get_documents().get_(self._current_batch_index)
        self._current_batch_index += 1
        self._overall_index += 1
        return self._current

    def get_master(self):
        return self._master

    def get_request(self):
        return self._request



