from abc import ABCMeta, abstractmethod


class ObjectIdentifiable(object):
    """
    Provides uniform access to objects that can supply an object identifier.
    This interface makes no guarantees about the thread-safety of implementations.
    However, wherever possible calls to this method should be thread-safe.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_object_id(self):
        """
        Gets the object identifier for this item.
        """
        pass


