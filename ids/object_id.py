from ids.comparable import Comparable
from ids.external_id_bundle import ExternalId
from ids.external_scheme import ExternalScheme
from ids.object_identifiable import ObjectIdentifiable
from ids.scheme import Scheme,IdValue
from ids.str_utils import StringUtils
from ids.unique_identifiable import UniqueIdentifiable


class ObjectId(ObjectIdentifiable):
    def __init__(self,
                 scheme=None,
                 value=None):
        super(ObjectId, self).__init__()
        self._scheme = Scheme.of(scheme)
        self._value = IdValue.of(value)

    def get_scheme(self):
        return self._scheme

    def set_object_id(self, object_id):
        self._object_id = object_id

    def get_value(self):
        return self._value

    def get_object_id(self):
        return self

    def at_version(self, version):
        return UniqueId.of(scheme=self.get_scheme(),
                           value=self.get_value(),
                           version=version)

    @classmethod
    def of(cls,
           scheme,
           value):
        return ObjectId(scheme, value)

    @classmethod
    def parse(cls, st):
        if not '~' in st:
            st = st.replace('::','~')
        split = st.split(st, '~')
        if len(split) == 2:
            return cls.of(scheme=split[0],
                          value=split[1])
        else:
            raise TypeError("Invalid identifier format: " + st)


    def __eq__(self, other):
        return self._scheme == other._scheme and \
            self._value == other._value

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        if self._scheme.__cmp__(other._scheme) == 0:
            return self._value.__cmp__(other._value)
        else:
            return self._scheme.__cmp__(other._scheme)

    def __str__(self):
        return self._scheme + '~' + self._value.__str__()

    def __hash__(self):
        return hash((self._scheme, self._value))

    def with_scheme(self, scheme):
        return ObjectId.of(scheme=scheme,
                           value=self.get_value())

    def with_value(self, value):
        return ObjectId.of(scheme=self._scheme,
                           value=value)


class UniqueId(UniqueIdentifiable, ObjectIdentifiable, Comparable):
    """
    An immutable unique identifier for an item.
    This identifier is used as a handle within the system to refer to an item uniquely.
    All versions of the same object share an {@link ObjectId} with the
    Many external identifiers, represented by {@link ExternalId}, are not truly unique.
    This {@code ObjectId} and {@code UniqueId} are unique within the OpenGamma instance.
    The unique identifier is formed from three parts, the scheme, value and version.
    The scheme defines a single way of identifying items, while the value is an identifier
    within that scheme. A value from one scheme may refer to a completely different
    real-world item than the same value from a different scheme.
    The version allows the object being identifier to change over time.
    If the version is null then the identifier refers to the latest version of the object.
    Note that some data providers may not support versioning.
    Real-world examples of {@code UniqueId} include instances of:
    <li>Database key - DbSec~123456~1</li>
     <li>In memory key - MemSec~123456~234</li>

     This class is immutable and thread-safe.

    EXTERNAL_SCHEME: Identification scheme for the unique identifier.
    This allows a unique identifier to be stored and passed using an {@code ExternalId}.
    """
    EXTERNAL_SCHEME = ExternalScheme.of('UID')

    def __init__(self,
                 scheme=None,
                 value=None,
                 version=None):
        """
            _scheme: String: The scheme that categorizes the identifier value.
            _value: String: The identifier value within the scheme.
            _version: String: The version of the identifier, null if latest or not-versioned.

            __eq__
            equal_object_id
            get_object_id
            get_scheme
            get_value
            get_version
            of
            parse
            set_scheme
            set_value
            set_version
        """
        self._scheme = Scheme.of(scheme)
        self._value = IdValue.of(value)
        self._version = version

    @classmethod
    def of(cls,
           object_id=None,
           version=None,
           external_id=None,
           scheme=None,
           value=None):
        """
        acceptable combinations:
            scheme, value
            scheme, value, version
            objectId, version
            externalId

        """
        if object_id:
            return UniqueId(object_id.get_scheme(),
                            object_id.get_value(),
                            version)
        elif external_id:
            return UniqueId(scheme=external_id.get_scheme(),
                            value=external_id.get_value())
        else:
            assert scheme is not None
            assert value is not None
            return UniqueId(scheme=scheme,
                            value=value,
                            version=version)

    @classmethod
    def parse(cls, st):
        print st
        if '~' not in st:
            st = st.replace('::','~')
        split = st.split('~')
        if len(split) == 2:
            return cls.of(scheme=split[0],
                          value=split[1],
                          version=None)
        elif len(split) == 3:
            return cls.of(scheme=split[0],
                          value=split[1],
                          version=split[2])
        else:
            raise Exception

    def get_scheme(self):
        """
        Gets the scheme of the identifier.
        """
        return self._scheme

    def get_value(self):
        """
        Gets the value of the identifier.
        """
        return self._value

    def get_version(self):
        """
        Gets the version of the identifier.
        """
        return self._version

    def with_scheme(self, scheme):
        return UniqueId.of(scheme=scheme,
                           value=self.get_value(),
                           version=self.get_version())

    def with_version(self, version):
        return UniqueId.of(scheme=self.get_scheme(),
                           value=self.get_value(),
                           version=version)

    def with_value_prefix(self, prefix):
        return UniqueId.of(scheme=self.get_scheme(),
                           value=prefix + self.get_value(),
                           version=self.get_version())

    def get_object_id(self):
        return ObjectId.of(scheme=self.get_scheme(),
                           value=self.get_value())

    def get_unique_id(self):
        return self

    def is_latest(self):
        return self._version is None

    def is_versioned(self):
        return self._version is not None

    def to_latest(self):
        """
        Returns a unique identifier based on this with the version set to null.
        """
        if self.is_versioned():
            return UniqueId(self.get_scheme(),
                            self.get_value(),
                            None)
        return self

    def to_external_id(self):
        return ExternalId.of(scheme=self._scheme, value=self._value)

    # def set_scheme(self, scheme):
    #     self._scheme = scheme
    #
    # def set_value(self, value):
    #     self._value = value
    #
    # def set_version(self, version):
    #     self._version = version

    def equal_object_id(self, other):
        """
        @param: other: ObjectIdentifiable
        @returns: boolean
        """
        if other is None:
            return False
        object_id = other.get_object_id()
        return self._scheme == object_id.get_scheme() and \
            self._value == object_id.get_value()

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, UniqueId):
            return self._scheme == other._scheme and \
                self._value == other._value and \
                self._version == other._version
        return False

    def __cmp__(self, other):
        comp = StringUtils.compare(self._scheme, other._scheme)
        if comp != 0:
            return comp
        comp = StringUtils.compare(self._value, other._value)
        if comp != 0:
            return comp
        return StringUtils.compare_with_null_low(self._version, other._version)

    def __str__(self):
        return self._scheme.__str__() + '~' + self._value.__str__() + '~' + self._version.__str__()

    def __hash__(self):
        return hash(self._scheme) ^ hash(self._value) ^ hash(self._version)

    def to_msg(self):
        raise NotImplementedError()

    @classmethod
    def from_msg(cls, deserializer, msg):
        raise NotImplementedError