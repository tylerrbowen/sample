from ids.comparable import Comparable
from utils.bp.instant import Instant


class VersionCorrection(Comparable):
    """
    An immutable version-correction combination.
    History can be stored in two dimensions and the version-correction provides the key. The first historic dimension is the classic series of versions. Each new version is stored in such a manor that
    previous versions can be accessed. The second historic dimension is corrections. A correction occurs when it is realized that the original data stored was incorrect.
    A fully versioned object in an OpenGamma installation will have a single state for any combination of version and correction. This state is assigned a version string which is used as the third
    component in a {@link UniqueId}, where all versions share the same {@link ObjectId}.
    This class represents a single version-correction combination suitable for identifying a single state. It is typically used to obtain an object, while the version string is used in the response.
    This class is immutable and thread-safe.
    """
    def __init__(self,
                 version_as_of=None,
                 corrected_to=None):
        """
        Creates a version-correction combination.
        :param version_as_of: datetime
        :param corrected_to: datetime
        """
        self._version_as_of = version_as_of
        self._corrected_to = corrected_to

    @classmethod
    def LATEST(cls):
        return VersionCorrection()

    @classmethod
    def of(cls,
           version_correction=None,
           version_as_of=None,
           corrected_to=None):
        if version_correction:
            return version_correction
        elif version_as_of or corrected_to:
            return VersionCorrection(version_as_of, corrected_to)
        else:
            return cls.LATEST()

    @classmethod
    def of_version_as_of(cls, version_as_of):
        return cls.of(version_as_of=version_as_of,
                      corrected_to=None)

    @classmethod
    def of_corrected_to(cls, corrected_to):
        return cls.of(version_as_of=None,
                      corrected_to=corrected_to)

    @classmethod
    def parse(cls, vc_str):
        pos_c = vc_str.index('.C')
        if vc_str[0] != 'V' or pos_c < 0:
            raise Exception
        ver_str = vc_str[1:pos_c]
        corr_str = vc_str[pos_c+2:]
        version_as_of = cls.parse_instant_string(ver_str)
        corrected_to = cls.parse_instant_string(corr_str)
        return cls.of(version_as_of=version_as_of,
                      corrected_to=corrected_to)

    @classmethod
    def parse_instant_string(cls, inst_str):
        """
        Parses a version-correction {@code Instant} from a standard string representation.
        The string representation must be either {@code LATEST} for null, or the ISO-8601 representation of the desired {@code Instant}.
        @param instantStr the instant string, null treated as latest
        @return the instant, not null
        """
        #return dt.datetime.strptime(inst_str, '%Y-%m-%d %H:%M:%S')
        if inst_str is None or inst_str.__eq__('LATEST'):
            return None
        else:
            try:
                return Instant.parse(inst_str)
            except TypeError, e:
                raise TypeError(e)



    def get_version_as_of(self):
        return self._version_as_of

    def get_corrected_to(self):
        return self._corrected_to

    def with_version_as_of(self, version_as_of):
        return VersionCorrection(version_as_of=version_as_of,
                                 corrected_to=self._corrected_to)

    def with_corrected_to(self, corrected_to):
        return VersionCorrection(version_as_of=self._version_as_of,
                                 corrected_to=corrected_to)

    def contains_latest(self):
        return self._version_as_of is None or self._corrected_to is None

    def with_latest_fixed(self, now):
        if self.contains_latest():
            if self._version_as_of is None:
                vao = now
            else:
                vao = self._version_as_of
            if self._corrected_to is None:
                ct = now
            else:
                ct = self._corrected_to
            return VersionCorrection(version_as_of=vao,
                                     corrected_to=ct)
        else:
            return self

    def get_version_as_of_string(self):
        if self._version_as_of is None:
            return 'LATEST'
        else:
            return self._version_as_of.__str__()

    def get_corrected_to_string(self):
        if self._corrected_to is None:
            return 'LATEST'
        else:
            return self._corrected_to.__str__()

    def __cmp__(self, other):
        cmp = self._version_as_of.__cmp__(other._version_as_of)
        if cmp != 0:
            return cmp
        else:
            return self._corrected_to.__cmp__(other._corrected_to)

    def __eq__(self, other):
        if not isinstance(other, VersionCorrection):
            return False
        return self._version_as_of == other._version_as_of and \
            self._corrected_to == other._corrected_to

    def __str__(self):
        return 'V' + self.get_version_as_of_string() + '.C' + self.get_corrected_to_string()




