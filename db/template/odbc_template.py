from accessor import Accessor
from db_operations import DBOperations, QueryCursorStatementCallback, UpdateCursorStatementCallback, \
    BatchUpdateCursorStatementCallback
from datasource_utils import DataSourceUtils
from single_value_extractors import SingleValueExtractor

class ODBCTemplate(Accessor, DBOperations):
    """
    <b>This is the central class in the JDBC core package.</b>
    It executes core JDBC workflow, leaving application code to provide SQL
    and extract results. This class executes SQL queries or updates, initiating
    iteration over ResultSets and catching JDBC exceptions and translating
    them to the generic, more informative exception hierarchy defined in the
    {@code org.springframework.dao} package.
    """

    RETURN_RESULT_SET_PREFIX = "#result-set-"
    RETURN_UPDATE_COUNT_PREFIX = "#update-count-"

    def __init__(self,
                 data_source = None):
        super(ODBCTemplate, self).__init__()
        self.set_data_source(data_source)
        self._native_extractor = None
        self._ignore_warnings = True
        self._fetch_size = 0
        self._max_rows = 0
        self._query_timeout = 0
        self._skip_results_processing = False
        self._skip_undeclared_results = False
        self._result_map_case_insensitive = False

    def set_fetch_size(self, fetch_size):
        self._fetch_size = fetch_size

    def get_fetch_size(self):
        return self._fetch_size

    def set_max_rows(self, max_rows):
        self._max_rows = max_rows

    def set_query_timeout(self, timeout):
        self._query_timeout = timeout

    def get_query_timeout(self):
        return self._query_timeout

    def set_ignore_warnings(self, ignore_warnings):
        self._ignore_warnings = ignore_warnings

    def is_ignore_warnings(self):
        return self._ignore_warnings

    def set_skip_results_processing(self, skip_results_processing):
        self._skip_results_processing = skip_results_processing

    def set_skip_undeclared_results(self, undeclared_results):
        self._skip_undeclared_results = undeclared_results

    def is_skip_undeclared_results(self):
        return self._skip_undeclared_results

    def set_result_map_case_insensitive(self, result_map_case_insensitive):
        self._result_map_case_insensitive = result_map_case_insensitive

    def is_result_map_case_insensitive(self):
        return self._result_map_case_insensitive

    def execute_action(self, sql, executor, call_back_action=None):
        if not isinstance(sql, basestring):
            sql, args = sql
        else:
            args = tuple()
        con = DataSourceUtils.get_connection(self.get_data_source())
        try:
            result = executor.do_in_cursor(con.cursor(), sql, args, call_back_action)
        except Exception, ex:
            result = []
        return result

    def query(self, sql, rse=None, rch=None, row_mapper=None):
        """
        rse: ResultSetExctractor: only implementation
        """
        if rse is not None:
            return self.execute_action(sql, QueryCursorStatementCallback(), rse)
        elif rch is not None:
            return self.execute_action(sql, rch)
        elif row_mapper is not None:
            return self.execute_action(sql, row_mapper)
        else:
            raise Exception

    def update(self, sql, *args, **kwargs):
        return self.execute_action(sql, UpdateCursorStatementCallback())

    def batch_update(self, sql, sql_args_list, *args, **kwargs):
        return self.execute_action((sql, sql_args_list), BatchUpdateCursorStatementCallback())










