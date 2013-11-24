from utils.bp.date_time_exception import DateTimeException


class ValueRange(object):
    def __init__(self,
                 min_smallest,
                 min_largest,
                 max_smallest,
                 max_largest):
        self.min_smallest = min_smallest
        self.min_largest = min_largest
        self.max_smallest = max_smallest
        self.max_largest = max_largest

    @classmethod
    def of(cls, min_smallest, max_largest, max_smallest=None, min_largest = None):
        if not max_smallest:
            max_smallest = max_largest
            min_largest = min_smallest
        return ValueRange(min_smallest, min_largest, max_smallest, max_largest)

    def get_minimum(self):
        return self.min_smallest

    def get_largest_minimum(self):
        return self.min_largest

    def get_smallest_minimum(self):
        return self.max_smallest

    def get_maximum(self):
        return self.max_largest

    def is_valid_value(self, value):
        return value >= self.get_minimum() and value <= self.get_maximum()

    def check_valid_value(self, value, field):
        return self.is_valid_value(value)

    def check_valid_int_value(self, value, field):
        if not self.is_valid_int_value(value):
            raise DateTimeException('invalid int value for ' + field.get_name() + ': ' + value.__str__())
        return int(value)

    def is_int_value(self):
        return self.get_minimum() >= -0x80000000 and self.get_maximum() <= 0x7fffffff

    def is_valid_int_value(self, value):
        return self.is_int_value() and self.is_valid_value(value)

    def __eq__(self, other):
        return self.min_smallest == other.min_smallest and \
            self.max_smallest == other.max_smallest and \
            self.min_largest == other.min_largest and \
            self.max_largest == other.max_largest

    def __hash__(self):
        return hash(self.min_smallest) ^ hash(self.max_smallest) ^ hash(self.min_largest) ^ hash(self.max_largest)

    def __str__(self):
        return str(self.min_smallest) + \
               '/' + str(self.min_largest) + \
               '/' + str(self.max_smallest) + \
               '/' + str(self.max_largest)



