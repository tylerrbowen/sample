from ids.object_id import ObjectId
from utils.supplier import Supplier
from atomic import Atomic


class ObjectIdSupplier(Supplier):
    """
    A supplier of object identifiers.
    An object identifier consists of a scheme and value.
    This class creates object identifiers for a fixed scheme name, where each
    value is an incrementing number. The values are created in a thread-safe way.
    This class is thread-safe and not externally mutable.
    """
    def __init__(self,
                 scheme):
        self._scheme = scheme
        self._id_count = Atomic(0)

    def get(self):
        new_id = self._id_count.update(lambda v: v + 1)
        return ObjectId.of(self._scheme, str(new_id))

    def get_with_value_prefix(self, value_prefix):
        new_id = self._id_count.update(lambda v: v + 1)
        return ObjectId.of(self._scheme, value_prefix + str(new_id))

    def __str__(self):
        return 'ObjectIdSupplier[' + self._scheme + ']'