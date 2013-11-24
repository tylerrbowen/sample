

class TransactionDefinition(object):
    """
    Interface that defines Spring-compliant transaction properties.

    """
    PROPAGATION_REQUIRED = 0
    PROPAGATION_SUPPORTS = 1
    PROPAGATION_MANDATORY = 2
    PROPAGATION_REQUIRES_NEW = 3

    PROPAGATION_NOT_SUPPORTED = 4
    PROPAGATION_NEVER = 5
    PROPAGATION_NESTED = 6
    ISOLATION_DEFAULT = -1
    TIMEOUT_DEFAULT = -1
    def __init__(self):
        return

    def get_propagation_behavior(self):
        pass

    def get_isolation_level(self):
        pass

    def get_timeout(self):
        pass

    def is_read_only(self):
        pass

    def get_name(self):
        pass


