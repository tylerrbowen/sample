from abc import ABCMeta, abstractmethod


class Entry(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_key(self):
        pass

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def set_key(self, key):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass



class SimpleImmutableEntry(Entry):
    def __init__(self, key, value):
        super(SimpleImmutableEntry, self).__init__()
        self._key = key
        self._value = value

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def set_value(self, value):
        raise Exception

    def set_key(self, key):
        raise Exception

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        return self.get_value() == other.get_value() and \
            self.get_key() == other.get_key()

    def __hash__(self):
        return self.get_value().__hash__() ^ self.get_key().__hash__()
