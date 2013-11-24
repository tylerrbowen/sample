

class SmartTransactionObject(object):

    def is_rollback_only(self):
        pass

    def flush(self):
        pass



class SavepointManager(object):

    def create_savepoint(self):
        pass

    def rollback_to_savepoint(self, savepoint):
        pass

    def release_savepoint(self, savepoint):
        pass


class ODBCTransactionObject(SmartTransactionObject, SavepointManager):
    def __init__(self):
        super(ODBCTransactionObject, self).__init__()
        self._connection_holder = None
        self._previous_isolation_level = None
        self._savepoint_allowed = False

    def set_connection_holder(self, connection_holder):
        self._connection_holder = connection_holder

    def get_connection_holder(self):
        return self._connection_holder

    def has_connection_holder(self):
        return self._connection_holder is not None

    def get_previous_isolation_level(self):
        return self._previous_isolation_level

    def set_previous_isolation_level(self, level):
        self._previous_isolation_level = level

    def set_savepoint_allowed(self, allowed):
        self._savepoint_allowed = allowed

    def is_savepoint_allowed(self):
        return self._savepoint_allowed

    def flush(self):
        pass

    def create_savepoint(self):
        pass

    def rollback_to_savepoint(self, savepoint):
        pass

    def release_savepoint(self, savepoint):
        pass

    def get_connection_holder_for_savepoint(self):
        return self._connection_holder
