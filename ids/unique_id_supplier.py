from ids.object_id import UniqueId
from utils.supplier import Supplier
from atomic import Atomic

__author__ = 'Tyler'


class UniqueIdSupplier(Supplier):
    def __init__(self,
                 scheme):
        super(UniqueIdSupplier, self).__init__()
        self._scheme = scheme
        self._id_count = Atomic(0)

    def get(self):
        new_id = self._id_count.update(lambda v: v + 1)
        return UniqueId.of(self._scheme, str(new_id))

    def get_with_value_prefix(self, value_prefix):
        new_id = self._id_count.update(lambda v: v + 1)
        return UniqueId.of(self._scheme, value_prefix + str(new_id))

    def __str__(self):
        return 'UniqueIdSupplier[' + self._scheme + ']'