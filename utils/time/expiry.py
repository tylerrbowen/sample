from utils.argument_checker import IllegalArgumentException
from expiry_accuracy import ExpiryAccuracy

class Expiry(object):

    def __init__(self, expiry, accuracy=None):
        """
        @param: ZonedDateTime: expiration date
        """
        self._expiry = expiry
        if accuracy is None:
            self._accuracy = ExpiryAccuracy.DAY_MONTH_YEAR
        else:
            self._accuracy = accuracy

    def get_expiry(self):
        return self._expiry

    def get_accuracy(self):
        return self._accuracy

    def to_instant(self):
        return self._expiry.to_instant()

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Expiry):
            return False
        if not self.get_accuracy() == other.get_accuracy():
            return False
        return self.equals_to_accuracy(self.get_accuracy(), self.get_expiry(), other.get_expiry())

    @classmethod
    def equals_to_accuracy(cls, accuracy, expiry_1, expiry_2):
        if accuracy == ExpiryAccuracy.MIN_HOUR_DAY_MONTH_YEAR:
            return expiry_1.get_minute() == expiry_2.get_minute() and \
                expiry_1.get_hour() == expiry_2.get_hour() and \
                expiry_1.get_day_of_month() == expiry_2.get_day_of_month() and \
                expiry_1.get_month() == expiry_2.get_month() and \
                expiry_1.get_year() == expiry_2.get_year()
        elif accuracy == ExpiryAccuracy.HOUR_DAY_MONTH_YEAR:
            return expiry_1.get_hour() == expiry_2.get_hour() and \
                expiry_1.get_day_of_month() == expiry_2.get_day_of_month() and \
                expiry_1.get_month() == expiry_2.get_month() and \
                expiry_1.get_year() == expiry_2.get_year()
        elif accuracy == ExpiryAccuracy.DAY_MONTH_YEAR:
            return expiry_1.get_day_of_month() == expiry_2.get_day_of_month() and \
                expiry_1.get_month() == expiry_2.get_month() and \
                expiry_1.get_year() == expiry_2.get_year()
        elif accuracy == ExpiryAccuracy.MONTH_YEAR:
            return expiry_1.get_month() == expiry_2.get_month() and \
                expiry_1.get_year() == expiry_2.get_year()
        elif accuracy == ExpiryAccuracy.YEAR:
            return expiry_1.get_year() == expiry_2.get_year()
        else:
            raise IllegalArgumentException('accuracy')

    def __hash__(self):
        return self._accuracy.__hash__() ^ self._expiry.__hash__()

    def __str__(self):
        if self._accuracy is not None:
            return 'Expiry ' + self._expiry.__str__() + ' accuracy ' + self._accuracy.name + ']'
        return 'Expiry ' + self._expiry.__str__()
