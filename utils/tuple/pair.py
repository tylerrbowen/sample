from abc import ABCMeta, abstractmethod
from utils.simple_immutable_entry import Entry
from first_then_second_doubles_pair_comparator import FirstThenSecondDoublesPairComparator


class Pair(Entry):
    """
    An immutable pair consisting of two elements.
    This implementation refers to the elements as 'first' and 'second'.
    The class also implements the {@code Map.Entry} interface where the key is 'first'
    """
    __metaclass__ = ABCMeta

    @classmethod
    def of(cls, first, second):
        return PairImpl(first, second)

    def get_key(self):
        return self.get_first()

    def get_value(self):
        return self.get_value()

    @abstractmethod
    def get_first(self):
        pass

    @abstractmethod
    def get_second(self):
        pass

    def set_key(self, key):
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()

    def to_list(self):
        lst = []
        lst.append(self.get_key())
        lst.append(self.get_value())
        return lst

    def __cmp__(self, other):
        return FirstThenSecondDoublesPairComparator.INSTANCE().compare(self, other)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Pair):
            return self.get_first() == other.get_first() and \
                self.get_second() == other.get_second()
        return False

    def __hash__(self):
        return self.get_first().__hash__() ^ self.get_second().__hash__()

    def __str__(self):
        s = ''
        s += '['
        s += ' ' + self.get_first().__str__() + ', '
        s += self.get_second().__str__() + ']'
        return s


class PairImpl(Pair):

    @classmethod
    def of(cls, first, second):
        return PairImpl(first, second)

    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get_second(self):
        return self.second

    def get_first(self):
        return self.first
