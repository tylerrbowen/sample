
from external_identifiable import ExternalIdentifiable
from comparable import Comparable
from external_scheme import ExternalScheme
from external_id_bundle import ExternalIdBundle
from str_utils import StringUtils


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
        return ExternalIdBundle.of(self)

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











