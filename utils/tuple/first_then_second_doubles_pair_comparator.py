

class FirstThenSecondDoublesPairComparator(object):

    @classmethod
    def INSTANCE(cls):
        return FirstThenSecondDoublesPairComparator()

    def compare(self, p1, p2):
        if p2 is None:
            return 1
        if p1.first == p2.first:
            if p1.second > p2.second:
                return 1
            elif p1.second < p2.second:
                return -1
            return 0
        if p1.first > p2.first:
            return 1
        return -1
