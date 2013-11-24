from external_id_search_type import ExternalIdSearchType
import numpy as np


class ExternalIdSearch(object):
    """
    A search request to match external identifiers.
    The search combines a set of external identifiers and a matching rule.
    This class is mutable and not thread-safe.

    """
    def __init__(self,
                 external_id=None,
                 external_ids=None,
                 search_type=None):
        """
        valid constructors:
        any single from the constructor or all None
        """
        self._external_ids = set()
        if search_type is not None:
            self.set_search_type(search_type)
        else:
            self._search_type = ExternalIdSearchType.ANY
        if external_id is not None:
            self.add_external_id(external_id)
        elif external_ids is not None:
            self.add_external_ids(external_ids)

    def get_external_ids(self):
        return sorted(self._external_ids)

    def get_search_type(self):
        return self._search_type.name

    def add_external_id(self, identifier):
        self._external_ids.add(identifier)

    def add_external_ids(self, identifiers):
        for idnt in identifiers:
            self._external_ids.add(idnt)

    def remove_external_id(self, identifier):
        self._external_ids.remove(identifier)

    def set_search_type(self, search_type):
        self._search_type = search_type

    def size(self):
        return len(self._external_ids)

    def __iter__(self):
        return self._external_ids.__iter__()

    def matches(self, other_id):
        if self._search_type == ExternalIdSearchType.EXACT:
            return len(self._external_ids) == 1 and other_id in self._external_ids
        elif self._search_type == ExternalIdSearchType.ALL:
            return self.contains_all(other_id)
        elif self._search_type == ExternalIdSearchType.ANY:
            return self.contains_any(other_id)
        elif self._search_type == ExternalIdSearchType.NONE:
            return not self.contains(other_id)
        else:
            return other_id in self._external_ids

    def contains_all(self, other_id_iter):
        for identifier in other_id_iter:
            if identifier not in self._external_ids:
                return False
        return True

    def contains_any(self, other_id_iter):
        for identifier in other_id_iter:
            if identifier in self._external_ids:
                return True
        return False

    def contains(self, external_id):
        return external_id is not None and \
               external_id in self._external_ids

    @classmethod
    def can_match(cls, external_id_search):
        if external_id_search is None:
            return True
        if external_id_search.get_search_type() == ExternalIdSearchType.NONE:
            return True
        return external_id_search.size() > 0

    def always_matches(self):
        return self.get_search_type() == ExternalIdSearchType.NONE \
            and self.size() == 0

    def __eq__(self, other):
        if not isinstance(other, ExternalIdSearch):
            return False
        return np.all(self._external_ids == other._external_ids)

    def __str__(self):
        s = 'Search['
        for eid in self._external_ids:
            s += eid.__str__() + ', '
        s = s[:-2]
        s += ']'
        return s

    def __hash__(self):
        h = 0
        for e_id in self._external_ids:
            h ^= e_id.__hash__()
        h ^= self._search_type.sort_order.__hash__()
        return h



