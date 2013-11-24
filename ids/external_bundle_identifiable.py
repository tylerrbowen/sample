from abc import ABCMeta, abstractmethod


class ExternalBundleIdentifiable(object):
    """
    Provides uniform access to objects that can supply a bundle of external identifiers.
    This interface makes no guarantees about the thread-safety of implementations.
    However, wherever possible calls to this method should be thread-safe.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_external_id_bundle(self):
        """
        Gets the external identifier bundle that define the security.
        Each external system has one or more identifiers by which they refer to the security.
        Some of these may be unique within that system, while others may be more descriptive.
        This bundle stores the set of these external identifiers.
        @return the bundle defining the security, not null
        """
        pass