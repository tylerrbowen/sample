from utils.bp.clock import Clock


class SharedClock(object):

    s_instance = Clock.system_utc()

    def __init__(self):
        return

    @classmethod
    def get_instance(cls):
        return cls.s_instance

    @classmethod
    def set_instance(cls, clock):
        cls.s_instance = clock