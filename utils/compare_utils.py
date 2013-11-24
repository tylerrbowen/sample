import numpy as np
__author__ = 'Tyler'


class CompareUtils(object):
    def __init__(self):
        pass

    @classmethod
    def max(cls, a, b):
        if a is not None and b is not None:
            if a.__cmp__(b) >= 0:
                return a
            else:
                return b
        if a is None:
            if b is None:
                return None
            return b
        return a

    @classmethod
    def min(cls, a, b):
        if a is not None and b is not None:
            if a.__cmp__(b) <= 0:
                return a
            else:
                return b
        if a is None:
            if b is None:
                return None
            return b
        return a

    @classmethod
    def compare_with_null_low(cls, a, b):
        if a is None:
            if b is None:
                return 0
            else:
                return -1
        elif b is None:
            return 1
        else:
            return a.__cmp__(b)

    @classmethod
    def compare_with_null_high(cls, a, b):
        if a is None:
            if b is None:
                return 0
            else:
                return 1
        elif b is None:
            return -1
        else:
            return a.__cmp__(b)

    @classmethod
    def close_equals(cls, a, b, max_difference=None):
        assert isinstance(a, float)
        assert isinstance(b, float)
        if np.isinf(a):
            return a == b
        if max_difference:
            assert isinstance(max_difference, float)
            return np.abs(a-b) < max_difference
        else:
            return np.abs(a-b) < 1e-15

    @classmethod
    def compare_with_tolerance(cls, a, b, max_difference):
        if np.isposinf(a):
            if a == b:
                return 0
            return 1
        elif np.isneginf(a):
            if a == b:
                return 0
            return -1
        elif np.isposinf(b):
            return -1
        elif np.isneginf(b):
            return 1
        if np.abs(a-b) < max_difference:
            return 0
        if a < b:
            return -1
        else:
            return 1

    @classmethod
    def compare_by_list(cls, lst, a, b):
        if a is None:
            if b is None:
                return 0
            else:
                return -1
        else:
            if b is None:
                return 1
            else:
                if a in lst and b in lst:
                    return lst.index(a) - lst.index(b)
                else:
                    return cls.commpare_with_null_low(a.__str__(), b.__str__())






