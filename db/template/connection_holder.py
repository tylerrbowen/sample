from resource_holder import ResourceHolderSupport


from connection_handle import SimpleConnectionHandle

class ConnectionHolder(ResourceHolderSupport):

    def __init__(self,
                 connection_handle=None,
                 connection=None,
                 transaction_active=False):
        super(ConnectionHolder, self).__init__()
        self._current_connection = None
        self._savepoints_supported = False
        self._savepoint_counter = 0
        if connection_handle:
            self._connection_handle = connection_handle
        else:
            self._connection_handle = SimpleConnectionHandle(connection)
        self._transaction_active = transaction_active

    def get_connection_handle(self):
        return self._connection_handle

    def has_connection(self):
        return self._connection_handle is not None

    def set_transaction_active(self, transaction_active):
        self._transaction_active = transaction_active

    def is_transaction_active(self):
        return self._transaction_active

    def set_connection(self, connection):
        if self._current_connection is not None:
            self._connection_handle.release_connection(self._current_connection)
            self._current_connection = None
        if connection is not None:
            self._connection_handle = SimpleConnectionHandle(connection)
        else:
            self._connection_handle = None

    def get_connection(self):
        if self._current_connection is None:
            self._current_connection = self._connection_handle.get_connection()
        return self._current_connection

    def released(self):
        super(ConnectionHolder, self).released()
        if not self.is_open() and self._current_connection is not None:
            self._connection_handle.release_connection(self._current_connection)
            self._current_connection = None

    def clear(self):
        super(ConnectionHolder, self).clear()
        self._transaction_active = False
        self._savepoint_counter = 0
        self._savepoints_supported = False


