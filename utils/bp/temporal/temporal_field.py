from abc import ABCMeta, abstractmethod


class TemporalField(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @abstractmethod
    def get_base_unit(self):
        raise NotImplementedError

    @abstractmethod
    def get_range_unit(self):
        raise NotImplementedError

    @abstractmethod
    def range(self):
        raise NotImplementedError

    @abstractmethod
    def is_supported_by(self, temporal):
        raise NotImplementedError

    @abstractmethod
    def range_refined_by(self, temporal):
        raise NotImplementedError

    @abstractmethod
    def get_from(self, temporal):
        raise NotImplementedError

    @abstractmethod
    def adjust_into(self, temporal, new_value):
        raise NotImplementedError

    @abstractmethod
    def resolve(self, temporal, value):
        raise NotImplementedError


