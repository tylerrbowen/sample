

class DateTimeException(RuntimeError):
    """
    Exception used to indicate a problem while calculating a date-time.
    This exception is used to indicate problems with creating, querying
    and manipulating date-time objects.

    """
    def __init__(self,
                 message,
                 cause=None):
        super(DateTimeException, self).__init__(message, cause)


