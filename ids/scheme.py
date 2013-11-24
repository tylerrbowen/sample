from external_scheme import ExternalScheme


class Scheme(str):
    def __cmp__(self, other):
        len1 = len(self)
        len2 = len(other)
        lim = min(len1, len2)
        k = 0
        while k < lim:
            c1 = self[k]
            c2 = other[k]
            if ord(c1) != ord(c2):
                return ord(c1) - ord(c2)
            k += 1
        return len1 - len2

    @classmethod
    def of(cls, scheme):
        if isinstance(scheme, Scheme):
            return scheme
        elif isinstance(scheme, basestring):
            return Scheme(scheme)
        elif isinstance(scheme, ExternalScheme):
            return Scheme(scheme.get_name())


class IdValue(str):
    def __cmp__(self, other):
        len1 = len(self)
        len2 = len(other)
        lim = min(len1, len2)
        k = 0
        while k < lim:
            c1 = self[k]
            c2 = other[k]
            if ord(c1) != ord(c2):
                return ord(c1) - ord(c2)
            k += 1
        return len1 - len2

    @classmethod
    def of(cls, id_value):
        if isinstance(id_value, IdValue):
            return id_value
        elif isinstance(id_value, basestring):
            return IdValue(id_value)