from ids.object_id import UniqueId
from mutable_unique_identifiable import MutableUniqueIdentifiable
from object_identifiable import ObjectIdentifiable
from iterable import Iterable
from object_id import ObjectId


class IdUtils:

    @classmethod
    def set_into(cls, obj, unique_id):
        """
        Sets the unique identifier of an object if it implements {@code MutableUniqueIdentifiable}.
        This provides uniform access to objects that support having their unique identifier
        updated after construction.
        For example, code in the database layer will need to update the unique identifier
        when the object is stored.

        @param object  the object to set into
        @param uniqueId  the unique identifier to set, may be null
        """
        if isinstance(obj, MutableUniqueIdentifiable):
            obj.set_unique_id(unique_id)

    @classmethod
    def to_string_list(cls, ids):
        """
        Converts a list of {@code UniqueId} or {@code ObjectId} to a list of strings.
        @param ids  the ids to convert, null returns empty list
        @return the string list, not null
        """
        strs = []
        if ids is not None:
            if not isinstance(ids, Iterable):
                raise TypeError('ids must be an iterable element')
            for obj in ids:
                if isinstance(obj, UniqueId):
                    strs.append(obj.__str__())
                elif isinstance(obj, ObjectIdentifiable):
                    strs.append(obj.get_object_id().__str__())
                else:
                    raise TypeError('Must be Object Identifiable Elements in list')
        return strs

    @classmethod
    def parse_unique_ids(cls, unique_id_strs):
        """
        Converts a list of strings to a list of {@code UniqueId}.
        @param uniqueIdStrs  the identifiers to convert, null returns empty list
        @return the list of unique identifiers, not null
        """
        unique_ids = []
        if unique_id_strs is not None:
            for unique_id_str in unique_id_strs:
                unique_ids.append(UniqueId.parse(unique_id_str))
        return unique_ids

    @classmethod
    def parse_object_ids(cls, object_id_strs):
        """
        Converts a list of strings to a list of {@code ObjectId}.
        @param objectIdStrs  the identifiers to convert, null returns empty list
        @return the list of unique identifiers, not null
        """
        object_ids = []
        if object_id_strs is not None:
            for object_id_str in object_id_strs:
                object_ids.append(ObjectId.parse(object_id_str))
        return object_ids

    @classmethod
    def is_within_time_bounds(cls, as_of, from_time, to_time):
        """
        Returns true if asOf instant is between from and to instants
        @param asOf the asOf instant
        @param from the from instant
        @param to the from instant
        @return asOf instant is between from and to instants
        """
        return (as_of is None and to_time is None) or \
               (to_time is None or to_time.is_after(as_of)) and (from_time is None or not from_time.is_after(as_of))

    @classmethod
    def is_version_correction(cls, vc, version_from, version_to, correction_from, correction_to):
        """
        Retruns true if the version-corrections is bounded by given instants
        @param vc the version-correction
        @param versionFrom the version from instant
        @param versionTo the version to instant
        @param correctionFrom the correction from instant
        @param correctionTo the correction from instant
        @return the version-corrections is bounded by given instants
        """
        return cls.is_within_time_bounds(vc.get_version_as_of(),
                                         version_from,
                                         version_to) and \
            cls.is_within_time_bounds(vc.get_version_corrected_to(),
                                      correction_from,
                                      correction_to)



