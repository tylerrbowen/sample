

from default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from utils.bp.temporal.temporal import Temporal
from abc import ABCMeta


class DefaultInterfaceTemporal(DefaultInterfaceTemporalAccessor, Temporal):
    __metaclass__ = ABCMeta

    def with_adjuster(self, adjuster):
        return adjuster.adjust_into(self)

    def plus_temporal(self, temporal_amount):
        return temporal_amount.add_to(self)

    def minus_temporal(self, temporal_amount):
        return temporal_amount.subtract_from(self)

    def minus(self, amount=None, unit=None):
        if amount == 0x8000000000000000L:
            return self.plus(0x7fffffffffffffffL, unit).plus(1, unit)
        else:
            return self.plus(-amount, unit)

