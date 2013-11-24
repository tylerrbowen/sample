from abc import ABCMeta, abstractmethod

class MutableUniqueIdentifiable(object):
    """
    Provides uniform access to objects that support having their unique identifier
    updated after construction.
    For example, code in the database layer will need to update the unique identifier
    when the object is stored.
    This interface makes no guarantees about the thread-safety of implementations.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_unique_id(self, unique_id):
        """
        Sets the unique identifier for this item.
        @param uniqueId  the unique identifier to set, not null
        """
        pass