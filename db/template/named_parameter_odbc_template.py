from db_operations import QueryCursorStatementCallback, UpdateCursorStatementCallback, \
    BatchUpdateCursorStatementCallback
from named_parameter_operations import NamedParameterODBCOperations
from odbc_template import ODBCTemplate
from named_parameter_utils import NamedParameterUtils
from db_map_sql_parameter_source import DbMapSqlParameterSource
from db.result_set_extractor import RowMapperResultSetExtractor
from db.template.rowmapper import SingleColumnRowMapper, ColumnMapRowMapper


class NamedParameterODBCTemplate(NamedParameterODBCOperations):
    def __init__(self,
                 data_source=None):
        super(NamedParameterODBCTemplate, self).__init__()
        self._classic_template = ODBCTemplate(data_source)

    def get_odbc_operations(self):
        return self._classic_template

    def execute_action(self, sql, executor, call_back_action=None):
        return self.get_odbc_operations().execute_action(sql, executor, call_back_action)

    def execute_sql(self, sql, param_map, executor, call_back_action=None):
        if param_map is not None:
            sql = self.get_prepared_statement(sql, DbMapSqlParameterSource(values=param_map))
        return self.get_odbc_operations().execute_action(sql, executor, call_back_action)

    def get_prepared_statement(self, sql, param_source):
        parsed_sql = self.get_parsed_sql(sql)
        sql_to_use = NamedParameterUtils.substitute_named_parameters(parsed_sql, param_source)
        params = NamedParameterUtils.build_value_array(parsed_sql, param_source)
        return sql_to_use, params

    def get_parsed_sql(self, sql):
        parsed_sql = NamedParameterUtils.parse_sql_statement(sql)
        return parsed_sql

    def query(self, sql, param_map=None, rse=None, rch=None, row_mapper=None):
        """
        rse: ResultSetExtractor: only implementation
        """
        if param_map is not None:
            if isinstance(param_map, DbMapSqlParameterSource):
                sql = self.get_prepared_statement(sql, param_map)
            else:
                sql = self.get_prepared_statement(sql, DbMapSqlParameterSource(values=param_map))
        if rse is not None:
            return self.execute_action(sql, QueryCursorStatementCallback(), rse)
            #return self.execute_action(sql, QueryCursorStatementCallback(), rse)
        elif rch is not None:
            return self.execute_action(sql, rch)
        elif row_mapper is not None:
            return self.execute_action(sql, QueryCursorStatementCallback(), row_mapper)
        else:
            raise Exception

    def query_for_list(self, sql, param_map, rse=None, rch=None, row_mapper=None):
        if param_map is not None:
            if isinstance(param_map, DbMapSqlParameterSource):
                sql = self.get_prepared_statement(sql, param_map)
            elif isinstance(param_map, dict):
                sql = self.get_prepared_statement(sql, DbMapSqlParameterSource(values=param_map))
            else:
                raise Exception
        if rse is not None:
            return self.execute_action(sql,
                                       QueryCursorStatementCallback(),
                                       RowMapperResultSetExtractor(SingleColumnRowMapper()))
        elif rch is not None:
            return self.execute_action(sql,
                                       QueryCursorStatementCallback(),
                                       RowMapperResultSetExtractor(ColumnMapRowMapper()))
        elif row_mapper is not None:
            return self.execute_action(sql, QueryCursorStatementCallback(), row_mapper)
        else:
            return self.execute_action(sql,
                                       QueryCursorStatementCallback(),
                                       RowMapperResultSetExtractor(SingleColumnRowMapper()))


    def update(self, sql, param_map, *args, **kwargs):
        if param_map is not None:
            if isinstance(param_map, DbMapSqlParameterSource):
                sql = self.get_prepared_statement(sql, param_map)
            elif isinstance(param_map, dict):
                sql = self.get_prepared_statement(sql, DbMapSqlParameterSource(values=param_map))
            else:
                raise Exception
        return self.execute_action(sql, UpdateCursorStatementCallback())

    def batch_update(self, sql, sql_args_list, *args, **kwargs):
        input_args = []
        for a in sql_args_list:
            sql_, a_ = self.get_prepared_statement(sql, a)
            input_args.append(a_)
        if len(input_args) > 0:
            return self.execute_action((sql_, input_args), BatchUpdateCursorStatementCallback())
        return None



