from abc import abstractmethod, ABCMeta


class Comparable(object):
    """
    force subclasses to implement __cmp__
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __cmp__(self, other):
        raise NotImplementedError()