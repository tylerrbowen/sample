from abc import ABCMeta, abstractmethod


class Iterable(object):

    @abstractmethod
    def __iter__(self):
        pass
