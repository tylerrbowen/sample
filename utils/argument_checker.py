from collections import Sized, Iterable


class IllegalArgumentException(RuntimeError):
    def __init__(self,
                 message=None,
                 cause=None):
        super(IllegalArgumentException, self).__init__(message, cause)


class ArgumentChecker:

    @classmethod
    def is_true(cls, true_if_valid, message):
        try:
            if not true_if_valid:
                raise IllegalArgumentException(message)
        except ValueError:
            return all(true_if_valid)

    @classmethod
    def is_false(cls, false_if_valid, message, *args):
        if false_if_valid:
            raise IllegalArgumentException(message, *args)

    @classmethod
    def not_null(cls, parameter, name):
        if parameter is None:
            raise IllegalArgumentException('input param ' + name + ' must not be null')

    @classmethod
    def no_nulls(cls, parameter, name):
        cls.not_null(parameter, name)
        for i in range(len(parameter)):
            if parameter[i] is None:
                raise IllegalArgumentException('Input parameter array ' + name + ' must not contain null at index ' +
                                               i.__str__())

    @classmethod
    def not_empty(cls, parameter, name):
        if not isinstance(parameter, Sized):
            raise IllegalArgumentException('input param ' + name + ' must not be empty')
        if not isinstance(parameter, Iterable):
            raise IllegalArgumentException('input param ' + name + ' must be iterable')
        for p in parameter:
            if isinstance(p, Sized):
                if len(p) == 0:
                    raise IllegalArgumentException('input param ' + name + ' must not be empty')
                else:
                    cls.not_empty(p, name)

    @classmethod
    def no_nulls(cls, parameter, name):
        cls.not_null(parameter, name)
        for obj in parameter:
            if isinstance(obj, Iterable):
                for i in obj:
                    if i is None:
                        raise IllegalArgumentException('Input parameter iterable ' + name + ' must not contain null')
            elif obj is None:
                raise IllegalArgumentException('Input paramter iterable ' + name + ' must not contain null')

    @classmethod
    def not_negative(cls, parameter, name):
        if parameter < 0:
            raise IllegalArgumentException('Input parameter ' + name + ' must not be negative')

    @classmethod
    def not_negative_or_zero(cls, parameter, name):
        if parameter <= 0:
            raise IllegalArgumentException('Input parameter ' + name + ' must not be negative or zer')