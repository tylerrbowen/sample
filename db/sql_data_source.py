import pg8000
import pyodbc
from data_source import DataSource
from sql_connection import PostgresConnection


class PostgresDataSource(DataSource):
    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 database):
        super(PostgresDataSource, self).__init__()
        self._connection = PostgresConnection(host,
                                              port,
                                              user,
                                              password,
                                              database)

    def get_connection(self):
        if self._connection.is_closed():
            self._connection.open()
        return self._connection.get_connection()


class MSSQLDataSource(DataSource):
    def __init__(self, connection_string):
        super(MSSQLDataSource, self).__init__()
        self._connection_string = connection_string
        self._connection = None
        self._is_open = False

    def get_connection_string(self):
        return self._connection_string

    def get_connection(self):
        self._connection = pyodbc.connect(self.get_connection_string())
        self._is_open = True
        return self._connection

    def close(self):
        if self._is_open:
            self._connection.close()
        self._is_open = False

    def get_cursor(self):
        return self.get_connection().cursor()

    def is_open(self):
        return self._is_open






