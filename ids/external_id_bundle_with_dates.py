
from external_identifiable import ExternalIdentifiable
from comparable import Comparable
from external_id import ExternalId
from utils.bp.local_date import LocalDate
from external_id_bundle import ExternalId, ExternalIdBundle
import numpy as np


class ExternalIdBundleWithDates(Comparable):

    @classmethod
    def EMPTY(cls):
        return ExternalIdBundleWithDates()

    def __init__(self,
                 external_ids=None):
        if external_ids:
            self._external_ids = sorted(set(external_ids))
        else:
            self._external_ids = set()
        self._hash_code = 0

    @classmethod
    def of(cls,
           external_ids=None,
           bundle=None):
        if external_ids is not None:
            return ExternalIdBundleWithDates(external_ids)
        elif bundle is not None:
            identifiers = set()
            for identifier in bundle.iterator():
                identifiers.add(ExternalIdWithDates.of(identifier))
            return ExternalIdBundleWithDates(identifiers)
        else:
            raise TypeError('Must have either list of ids with dates or bundle of ids')

    @classmethod
    def create(cls, external_ids):
        lst = []
        for e_id in external_ids:
            new_eid = ExternalIdWithDates.of(e_id.get_external_id(), e_id.get_valid_from(), e_id.get_valid_to())
            lst.append(new_eid)
        return ExternalIdBundleWithDates(lst)

    def get_external_ids(self):
        return self._external_ids

    def with_external_id(self, external_id):
        ids = self._external_ids
        if external_id in ids:
            return self
        ids.add(external_id)
        return self.create(ids)

    def with_external_ids(self, external_ids):
        lst = []
        for e_id in external_ids:
            new_eid = ExternalIdWithDates.of(e_id.get_external_id(), e_id.get_valid_from(), e_id.get_valid_to())
            lst.append(new_eid)
        to_add = set(lst)
        contains = True
        for e_id in external_ids:
            if e_id not in to_add:
                contains = False
                break
        if not contains:
            for e_id in external_ids:
                to_add.add(e_id)
            return ExternalIdBundleWithDates(to_add)
        return self

    def size(self):
        return len(self._external_ids)

    def is_empty(self):
        return len(self._external_ids) == 0

    def iterator(self):
        return self._external_ids.__iter__()

    def __iter__(self):
        return self._external_ids.__iter__()

    def contains_all(self):
        pass

    def contains_any(self):
        pass

    def contains(self):
        pass

    def to_string_list(self):
        lst = []
        for e_id in self.iterator():
            lst.append(e_id.__str__())
        return lst

    def get_external_id_bundle(self):
        return self

    def to_bundle(self, valid_on):
        ids = set()
        for identifier in self._external_ids:
            if identifier.is_valid_on(valid_on):
                ids.add(identifier.to_external_id())
        return ExternalIdBundle.of(external_ids=ids)


    def __cmp__(self, other):
        my_set = self.get_external_ids()
        other_set = other.get_external_ids()
        if len(my_set) < len(other_set):
            return -1
        if len(my_set) > len(other_set):
            return 1
        my_lst = list(my_set)
        other_lst = list(other_set)
        for i in xrange(len(my_lst)):
            c = my_lst[i].__cmp__(other_lst[i])
            if c != 0:
                return c
        return 0

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ExternalIdBundle):
            return np.all(self._external_ids == other._external_ids)
        return False

    def __hash__(self):
        if self._hash_code == 0:
            for e_id in self._external_ids:
                self._hash_code ^= (31 + e_id.__hash__())
        return self._hash_code

    def __str__(self):
        s = 'BundleWithDates['
        for e_id in self._external_ids:
            s += e_id.__str__() + ', '
        s = s[:-2]
        s += ']'
        return s



class ExternalIdWithDates(ExternalIdentifiable, Comparable):
    """
    An immutable external identifier with validity dates.
    This class is used to restrict the validity of an {@link ExternalId external identifier}.
    This class is immutable and thread-safe.
    """
    def __init__(self,
                 identifier,
                 valid_from=None,
                 valid_to=None):
        """
        @param identifier  the identifier, not null
        @param valid_from the valid from date, may be null
        @param valid_to the valid to date, may be null
        """
        self._identifier = identifier
        self._valid_from = valid_from
        self._valid_to = valid_to

    @classmethod
    def of(cls,
           identifier,
           valid_from=None,
           valid_to=None):
        return ExternalIdWithDates(identifier,
                                   valid_from,
                                   valid_to)

    @classmethod
    def parse(cls, string):
        identifier = None
        valid_from = None
        valid_to = None
        start_pos = string.find('~S~')
        end_pos = string.find('~E~')
        if start_pos > 0:
            identifier = ExternalId.of(string[0:start_pos])
            if end_pos > 0:
                valid_from = LocalDate.parse(string[start_pos+3:end_pos])
                valid_to = LocalDate.parse(string[end_pos+3:])
            else:
                valid_from = LocalDate.parse(string[start_pos+3:])
        elif end_pos > 0:
            identifier = ExternalId.parse(string[0:end_pos])
            valid_to = LocalDate.parse(string[end_pos+3:])
        else:
            identifier = ExternalId.parse(string)
        return ExternalIdWithDates(identifier, valid_from, valid_to)

    def get_external_id(self):
        return self._identifier

    def get_valid_from(self):
        return self._valid_from

    def get_valid_to(self):
        return self._valid_to

    def is_valid_on(self, date):
        if date is None:
            return True
        from_date = self.get_valid_from() if self.get_valid_from() is not None else LocalDate.MAX()
        to_date = self.get_valid_to() if self.get_valid_to() is not None else LocalDate.MAX()
        return not date.is_before(from_date) and not date.is_after(to_date)

    def to_external_id(self):
        return self._identifier

    def __cmp__(self, other):
        return self._identifier.__cmp__(other._identifier)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ExternalIdWithDates):
            return self._identifier.__eq__(other._identifier) and \
                self._valid_from.__eq__(other._valid_from) and \
                self._valid_to.__eq__(other._valid_to)
        return False

    def __hash__(self):
        return self._identifier.__hash__() ^ self._valid_from.__hash__() ^ self._valid_to.__hash__()

    def __str__(self):
        s = self._identifier.__str__()
        if self._valid_from is not None:
            s += '~S~' + self._valid_from.__str__()
        if self._valid_to is not None:
            s += '~E~' + self._valid_to.__str__()
        return s





