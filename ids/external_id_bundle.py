from collections import Sequence
import numpy as np
from ids.external_bundle_identifiable import ExternalBundleIdentifiable
from external_identifiable import ExternalIdentifiable
from comparable import Comparable
from external_scheme import ExternalScheme
from str_utils import StringUtils


class ExternalIdBundle(ExternalBundleIdentifiable, Comparable):
    def __init__(self,
                 identifiers=None):
        if identifiers is None:
            self._external_ids = set()
        else:
            self._external_ids = sorted(set(identifiers))
        self._hash_code = 0

    @classmethod
    def EMPTY(cls):
        return ExternalIdBundle()

    @classmethod
    def of(cls,
           scheme=None,
           value=None,
           external_id=None,
           external_ids=None):
        """
        constructor combinations:
            scheme, value
            external_id
            external_ids
        """
        if scheme is not None and value is not None:
            return cls.of(external_id=ExternalId.of(scheme=scheme, value=value))
        elif external_id is not None:
            return ExternalIdBundle(set(sorted([external_id])))
        elif external_ids is not None:
            return ExternalIdBundle(set(sorted(external_ids)))
        else:
            raise Exception

    @classmethod
    def parse(cls, strs):
        assert(isinstance(strs, Sequence))
        external_ids = []
        for s in strs:
            external_ids.append(ExternalId.parse(s))
        return cls.create(external_ids)

    @classmethod
    def create(cls, external_ids):
        lst = []
        for e_id in external_ids:
            new_eid = ExternalId.of(e_id.get_scheme(), e_id.get_value())
            lst.append(new_eid)
        return ExternalIdBundle(
            lst
        )

    def get_external_id(self,
                        scheme):
        for identifier in self._external_ids:
            if identifier.get_scheme() == scheme:
                return identifier
        return None

    def get_external_ids(self,
                         scheme=None):
        if scheme:
            return_ids = set()
            for e_id in self._external_ids:
                if e_id.get_scheme() == scheme:
                    return_ids.add(e_id)
        else:
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
            new_eid = ExternalId.of(e_id.get_scheme(), e_id.get_value())
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
            return ExternalIdBundle(to_add)
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
        s = 'Bundle['
        for e_id in self._external_ids:
            s += e_id.__str__() + ', '
        s = s[:-2]
        s += ']'
        return s


class ExternalId(ExternalIdentifiable, Comparable):
    """
    An immutable external identifier for an item.
    This identifier is used as a handle within the system to refer to an externally defined identifier.
    By contrast, the {@code ObjectId} and {@code UniqueId} represent identifiers within an OpenGamma system.
    The external identifier is formed from two parts, the scheme and value.
    The scheme defines a single way of identifying items, while the value is an identifier
    within that scheme. A value from one scheme may refer to a completely different
    real-world item than the same value from a different scheme.
    Real-world examples of {@code ExternalId} include instances of:
        <li>Cusip</li>
        <li>Isin</li>
    This class is immutable and thread-safe.
    """
    def __init__(self,
                 scheme,
                 value):
        self._scheme = scheme
        self._value = value

    @classmethod
    def of(cls,
           scheme,
           value):
        if isinstance(scheme, basestring):
            scheme = ExternalScheme.of(scheme)
        return ExternalId(scheme, value)

    @classmethod
    def parse(cls, string):
        string = string.replace('::', '~')
        pos = string.find('~')
        if pos < 0:
            raise TypeError("Invalid identifier format: " + string)
        return ExternalId(ExternalScheme.of(string[0:pos]), string[pos + 1:])

    def get_scheme(self):
        return self._scheme

    def get_value(self):
        return self._value

    def is_scheme(self, scheme):
        if isinstance(scheme, basestring):
            return self._scheme.get_name().__eq__(scheme)
        return self._scheme.__eq__(scheme)

    def is_not_scheme(self, scheme):
        return not self.is_scheme(scheme)

    def get_external_id(self):
        return self

    def to_bundle(self):
        return ExternalIdBundle.of(external_id=self)

    def __cmp__(self, other):
        comp = self._scheme.__cmp__(other._scheme)
        if comp != 0:
            return comp
        return StringUtils.compare(self._value, other._value)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ExternalId):
            return self._scheme.__eq__(other._scheme) and \
                self._value.__eq__(other._value)
        return False

    def __hash__(self):
        return self._scheme.__hash__() ^ self._value.__hash__()

    def __str__(self):
        s = self._scheme.__str__() + '~' + self._value.__str__()
        return s

    def to_msg(self, serializer, msg):
        raise NotImplementedError()

    @classmethod
    def from_msg(cls, deserializer, msg):
        raise NotImplementedError()
