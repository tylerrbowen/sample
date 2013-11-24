__author__ = 'AH0137307'
from source.source_base import Source


class AbstractSource(Source):
    def __init__(self):
        super(AbstractSource, self).__init__()

    @classmethod
    def get(cls,
            source=None,
            unique_id=None,
            object_id=None,
            unique_ids=None,
            object_ids=None):
        """
            source, unique_ids
            source, object_ids, version_correction
        """
        if source is None:
            source = cls
        result = dict()
        if unique_ids:
            for unique_id in unique_ids:
                try:
                    obj = source.get(unique_id=unique_id)
                    result[unique_id] = obj
                except KeyError:
                    pass
            return result
        if object_ids:
            for object_id in object_ids:
                try:
                    obj = source.get(object_id=object_id)
                    result[object_id] = obj
                except KeyError:
                    pass
            return result


