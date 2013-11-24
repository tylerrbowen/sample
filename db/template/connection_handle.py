

class ConnectionHandle(object):

    def get_connection(self):
        pass

    def release_connection(self, con):
        pass



class SimpleConnectionHandle(ConnectionHandle):
    def __init__(self,
                 connection):
        self._connection = connection

    def get_connection(self):
        return self._connection

    def release_connection(self, con):
        pass

    def __str__(self):
        return 'SimpleConnectionHandle: ' + self._connection.__str__()
