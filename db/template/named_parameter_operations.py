from db_operations import DBOperations


class NamedParameterODBCOperations(object):
    """
    Interface specifying a basic set of JDBC operations allowing the use
    of named parameters rather than the traditional '?' placeholders.
    """

    def get_odbc_operations(self):
        """
        return: DBOperations
        """
        pass

    def execute_action(self, sql, executor, call_back_action=None):
        """
        String sql
        Map<String, ?> paramMap
        StatementCallback<T> action
        """
        pass

    def execute_sql(self, sql, param_map, executor, call_back_action=None):
        """
        Issue a single SQL execute, typically a DDL statement.
        """
        pass

    def query(self, sql, param_map, rse=None, rch=None, row_mapper=None):
        """
        String sql
        Map<String, ?> paramMap
        StatementCallback<T> action
        """
        pass

    def query_for_list(self, sql, param_map, *args, **kwargs):
        """
        Execute a query for a result list, given static SQL.
        """
        pass

    def query_for_map(self, sql, param_map, *args, **kwargs):
        """
        Execute a query for a result Map, given static SQL.
        """
        pass

    def update(self, sql, param_map, *args, **kwargs):
        """
        Issue a single SQL update operation (such as an insert, update or delete statement).
        """
        pass

    def batch_update(self, sql_list, param_map, *args, **kwargs):
        """
        Issue multiple SQL updates on a single JDBC Statement using batching.
        """
        pass

    def query_for_object(self, sql, param_map, *args, **kwargs):
        """
        Execute a query for a result object, given static SQL.
        """
        pass

    def query_for_int(self, sql, param_map, *args, **kwargs):
        """
        Execute a query for a result int, given static SQL.
        """
        pass

    def query_for_long(self, sql, param_map, *args, **kwargs):
        """
        Execute a query for a result long, given static SQL.
        """
        pass