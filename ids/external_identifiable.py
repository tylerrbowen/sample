from abc import ABCMeta, abstractmethod


class ExternalIdentifiable(object):
    """
    Provides uniform access to objects that can supply an external identifier.
    This interface makes no guarantees about the thread-safety of implementations.
    However, wherever possible calls to this method should be thread-safe.
    """
    __metaclass__ = ABCMeta


    @abstractmethod
    def get_external_id(self):
        """
        Gets the external identifier for the instance.
        @return the external identifier, may be null
        """
        pass