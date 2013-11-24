from utils.bp.clock import Clock

class PSClock(object):

    s_instance = Clock.system_utc()

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls):
        return cls.s_instance

    @classmethod
    def set_instance(cls, clock):
        cls.s_instance = clock

    @classmethod
    def get_zone(cls):
        return cls.s_instance.get_zone()

    @classmethod
    def set_zone(cls, zone):
        cls.s_instance = cls.s_instance.with_zone(zone)


