

class StringUtils:

    @classmethod
    def compare(cls, str1, str2):
        len1 = len(str1)
        len2 = len(str2)
        lim = min(len1, len2)
        k = 0
        while k < lim:
            c1 = str1[k]
            c2 = str2[k]
            if ord(c1) != ord(c2):
                return ord(c1) - ord(c2)
            k += 1
        return len1 - len2

    @classmethod
    def compare_with_null_low(cls, str1, str2):
        if str1 is None:
            if str2 is None:
                return 0
            else:
                return -1
        elif str2 is None:
            return 1
        else:
            return cls.compare(str1, str2)