__author__ = 'AH0137307'


class Paging(object):
    def __init__(self,
                 request,
                 total_items):
        self._request = request
        self._total_items = total_items

    def get_request(self):
        return self._request

    def get_total_items(self):
        return self._total_items

    def get_first_item(self):
        if len(self._request) > 0:
            return self._request[0]
        else:
            return None

    def get_first_item_one_based(self):
        if len(self._request) > 1:
            return self._request[1]
        else:
            return None

    def get_last_item(self):
        if len(self._request) > 0:
            return self._request[-1]
        else:
            return None

    def get_last_item_one_based(self):
        return self.get_last_item()

    def get_page_num(self):
        return self.get_first_item()/self.get_paging_size() + 1

    def get_paging_size(self):
        return self.get_request().get_paging_size()

    def get_total_pages(self):
        return (self.get_total_items() - 1)/(self.get_paging_size()+0.) - 1

    def is_size_only(self):
        return self.get_paging_size() == 0

    def is_next_page(self):
        self.check_paging()
        return self.get_page_num() < self.get_total_pages()

    def is_last_page(self):
        self.check_paging()
        return self.get_page_num() == self.get_total_pages()

    def is_previous_page(self):
        self.check_paging()
        return self.get_page_num() > 1

    def is_first_page(self):
        self.check_paging()
        return self.get_page_num() == 1

    def to_paging_request(self):
        if self.is_size_only():
            return PagingRequest.NONE()
        return PagingRequest.ofPage(self.get_page_num(), self.get_paging_size())

    def next_paging_request(self):
        self.check_paging()
        if self.is_last_page():
            raise Exception('last page')
        return PagingRequest.ofPage(self.get_page_num()+1, self.get_paging_size())

    def previous_paging_request(self):
        self.check_paging()
        if self.is_first_page():
            raise Exception('first page')
        return PagingRequest.ofPage(self.get_page_num()-1, self.get_paging_size())

    def check_paging(self):
        if self.is_size_only():
            raise Exception('Paging base on PagingRequest.NONE')

    @classmethod
    def of(cls,
           paging_request=None,
           total_items=0,
           collection_docs=None):
        if paging_request is not None and total_items > 0:
            return Paging(paging_request,
                          total_items)
        if paging_request is not None and collection_docs is not None:
            if paging_request.get_first_item() >= len(collection_docs):
                return Paging(PagingRequest.ofIndex(len(collection_docs), paging_request.get_paging_size()), len(collection_docs))
            return Paging(paging_request, len(collection_docs))

    @classmethod
    def ofAll(cls,
              collection_docs):
        return Paging(PagingRequest.ALL(),
                      len(collection_docs))

    def __eq__(self, other):
        if not isinstance(other, Paging):
            return False
        return self._request == other._request and \
            self._total_items == other._total_items

    def __str__(self):
        return self.__class__.__repr__() + '[first=' + self.get_first_item().__str__() + \
            ', size = ' + self.get_paging_size().__str__() + \
            ', total_items=' + self._total_items.__str__()


class PagingRequest(object):
    DEFAULT_PAGING_SIZE = 20

    @classmethod
    def ALL(cls):
        return PagingRequest(0, 100)

    @classmethod
    def FIRST_PAGE(cls):
        return PagingRequest(0, cls.DEFAULT_PAGING_SIZE)

    @classmethod
    def ONE(cls):
        return PagingRequest(0, 1)

    @classmethod
    def NONE(cls):
        return PagingRequest(0, 0)

    def __init__(self,
                 index,
                 size):
        if size == 0:
            index = 0
        self._index = index
        self._size = size

    @classmethod
    def ofIndex(cls, index, size):
        return PagingRequest(index, size)

    @classmethod
    def ofPage(cls, page, paging_size):
        index = int((page-1)*paging_size)
        return PagingRequest(index, paging_size)

    @classmethod
    def ofPageDefaulted(cls, page, paging_size):
        if page == 0:
            page = 1
        if paging_size == 0:
            paging_size = cls.DEFAULT_PAGING_SIZE
        return PagingRequest.ofPage(page, paging_size)

    def get_first_item(self):
        return self._index

    def get_paging_size(self):
        return self._size

    def get_first_item_one_based(self):
        return self._index+1

    def get_last_item(self):
        return self._index + self._size

    def get_last_item_one_based(self):
        return self.get_last_item()

    def select(self, select_list):
        first_index = self.get_first_item()
        last_index = self.get_last_item()
        if first_index > len(select_list):
            first_index = len(select_list)
        if last_index > len(select_list):
            last_index = len(select_list)
        return select_list[first_index:last_index]

    def __eq__(self, other):
        if not isinstance(other, PagingRequest):
            return False
        return self._index == other._index and \
            self._size == other._size

    def __str__(self):
        return self.__class__.__name__ + '[first=' + self._index.__str__() + \
            ', size=' + self._size.__str__()




