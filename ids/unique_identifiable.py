from abc import ABCMeta, abstractmethod


class UniqueIdentifiable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_unique_id(self):
        """
        Provides uniform access to objects that can supply a unique identifier.
        This interface makes no guarantees about the thread-safety of implementations.
        However, wherever possible calls to this method should be thread-safe.
        """
        pass