__author__ = 'AH0137307'


class TemporalUnit(object):
    def __init__(self):
        return

    def get_name(self):
        raise NotImplementedError

    def get_duration(self):
        raise NotImplementedError

    def is_duration_estimated(self):
        raise NotImplementedError

    def is_supported_by(self, *args, **kwargs):
        raise NotImplementedError

    def add_to(self, date_time, period_to_add):
        raise NotImplementedError

    def between(self, t1, t2):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


