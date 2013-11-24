
from connection import Connection
import pg8000


class PostgresConnection(Connection):
    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 database):
        super(PostgresConnection, self).__init__()
        self._connection = pg8000.dbapi.ConnectionWrapper(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database)
        self._is_closed = False
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database_name = database

    def get_connection(self):
        return self._connection

    def close(self):
        try:
            self.get_connection().close()
            self._is_closed = True
        except Exception:
            return False
        return True

    def commit(self):
        try:
            self.get_connection().commit()
        except Exception:
            return False
        return True

    def rollback(self):
        try:
            self.get_connection().rollback()
        except Exception:
            return False
        return True

    def get_cursor(self):
        return self.get_connection().cursor()

    def is_closed(self):
        return self._is_closed

    def open(self):
        self._connection = pg8000.dbapi.ConnectionWrapper(
            host=self.get_host(),
            port=self.get_port(),
            user=self.get_user(),
            password=self.get_password(),
            database=self.get_database_name())
        self._is_closed = False

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port

    def get_user(self):
        return self._user

    def get_password(self):
        return self._password

    def get_database_name(self):
        return self._database_name





