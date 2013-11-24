
from utils.bp.date_time_exception import DateTimeException


class DateTimeParseException(DateTimeException):

    def __init__(self, message, parsed_data, error_index, cause=None):
        super(DateTimeParseException, self).__init__(message, cause)
        self._parsed_data = parsed_data
        self._error_index = error_index

    def get_parsed_string(self):
        return self._parsed_data

    def get_error_index(self):
        return self._error_index

