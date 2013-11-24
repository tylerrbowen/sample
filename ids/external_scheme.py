from comparable import Comparable
from str_utils import StringUtils


class ExternalScheme(Comparable):
    """
    A classification scheme for external identifiers.
    The scheme defines a universe of identifier values.
    Each value only has meaning within that scheme, and the same value may have
    a different meaning in a different scheme.
    The scheme class is a type-safe wrapper on top of a string name.
    This class is immutable and thread-safe.
    """
    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    @classmethod
    def of(cls, name):
        return ExternalScheme(name)

    def __cmp__(self, other):
        return StringUtils.compare(self._name, other._name)

    def __eq__(self, other):
        if not isinstance(other, ExternalScheme):
            return False
        return self._name == other._name

    def __hash__(self):
        return hash(self._name)

    def __str__(self):
        return self._name
