from ids.object_id import ObjectId, UniqueId

__author__ = 'AH0137307'


class IdUtils(object):

    @classmethod
    def set_into(cls, object, unique_id):
        object.set_unique_id(unique_id)

    @classmethod
    def parse_unique_ids(cls, unique_id_strings):
        unique_ids = []
        for unique_id_str in unique_id_strings:
            unique_ids.append(UniqueId.parse(unique_id_str))
        return unique_ids

    @classmethod
    def parse_object_ids(cls, object_id_strings):
        object_ids = []
        for object_id_str in object_id_strings:
            object_ids.append(ObjectId.parse(object_id_str))
        return object_ids

    @classmethod
    def is_within_time_bounds(cls, as_of, from_time, to_time):
        return (as_of is None and to_time is None) or \
               (to_time is None or to_time < as_of) and \
               (from_time is None or from_time < as_of)

    @classmethod
    def is_version_correction(cls, vc, version_from, version_to, correction_from, correction_to):
        return cls.is_within_time_bounds(vc.get_version_as_of(),
                                         version_from,
                                         version_to) and \
            cls.is_within_time_bounds(vc.get_corrected_to(),
                                      correction_from,
                                      correction_to)


