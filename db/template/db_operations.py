import pyodbc
from datasource_utils import DataSourceUtils


class DBOperations(object):
    """
    Interface specifying a basic set of ODBC operations.
    """
    def execute_action(self, *args, **kwargs):
        pass

    def execute_sql(self, sql, *args, **kwargs):
        """
        Issue a single SQL execute, typically a DDL statement.
        """
        pass

    def query(self, sql, rse=None, rch=None, row_mapper=None):
        """
        sql: String
        rse: ResultSetExtractor
        rch: RowCallbackHandler
        row_mapper: RowMapper
        """
        pass

    def query_for_list(self, sql, *args, **kwargs):
        """
        Execute a query for a result list, given static SQL.
        """
        pass

    def query_for_map(self, sql, *args, **kwargs):
        """
        Execute a query for a result Map, given static SQL.
        """
        pass

    def update(self, sql, *args, **kwargs):
        """
        Issue a single SQL update operation (such as an insert, update or delete statement).
        """
        pass

    def batch_update(self, sql_list, *args, **kwargs):
        """
        Issue multiple SQL updates on a single JDBC Statement using batching.
        """
        pass

    def query_for_object(self, sql, *args, **kwargs):
        """
        Execute a query for a result object, given static SQL.
        """
        pass

    def query_for_int(self, sql, *args, **kwargs):
        """
        Execute a query for a result int, given static SQL.
        """
        pass

    def query_for_long(self, sql, *args, **kwargs):
        """
        Execute a query for a result long, given static SQL.
        """
        pass


class QueryCursorStatementCallback(object):

    def do_in_cursor(self, cursor, sql, sql_args, result_set_extractor):
        try:
            rs = cursor.execute(sql, sql_args).fetchall()
            return result_set_extractor.extract_data(rs)
        except pyodbc.ProgrammingError, e:
            print e.message
        finally:
            cursor.close()


class UpdateCursorStatementCallback(object):

    def do_in_cursor(self, cursor, sql, sql_args, *args):
        try:
            rc = cursor.execute(sql, sql_args).rowcount
            cursor.commit()
            return rc
        except pyodbc.ProgrammingError, e:
            print e.message
        finally:
            cursor.close()


class BatchUpdateCursorStatementCallback(object):

    def do_in_cursor(self, cursor, sql, sql_args_list, *args):
        result_list = []
        for sql_args in sql_args_list:
            try:
                rc = cursor.execute(sql, sql_args).rowcount
                result_list.append(rc)
            except pyodbc.ProgrammingError, e:
                print e.message
        cursor.commit()
        cursor.close()
        return result_list
