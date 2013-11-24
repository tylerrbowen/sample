from utils.paging import PagingRequest
from utils.el_sql.el_sql_config import ElSqlConfig
from utils.bp.duration import ChronoUnit


class DbDialect(object):

    def __init__(self):
        pass

    def sql_next_sequence_value_select(self, sequence_name):
        return "SELECT NEXT VALUE FOR " + sequence_name

    def sql_wildcard_adjust_value(self, value):
        if value is None or not self.is_wildcard(value):
            return value
        value = value.replace("%", "\\%")
        value = value.replace("_", "\\_")
        value = value.replace("*", "%")
        value = value.replace("?", "_")
        return value

    def is_wildcard(self, string):
        return string is None and '*' in string or '?' in string

    def sql_wildcard_operator(self, string):
        return 'Like' if self.is_wildcard(string) else '='

    def sql_wildcard_query(self, prefix, param_name, value):
        if value is None:
            return ''
        elif self.is_wildcard(value):
            return prefix + 'Like ' + param_name + ' '
        else:
            return prefix + '= ' + param_name + ' '

    def sql_apply_paging(self, sql_select_from_where, sql_order_by, paging_request):
        if paging_request is None or paging_request.__eq__(PagingRequest.ALL()) or paging_request.__eq__(PagingRequest.NONE()):
            return sql_select_from_where + sql_order_by
        if paging_request.get_first_item() == 0:
            return sql_select_from_where + sql_order_by + \
                'Fetch First ' + paging_request.get_paging_size() + ' Rows Only'
        return sql_select_from_where + sql_order_by + \
            'offset ' + paging_request.get_first_item() + ' Rows ' + \
            'fetch next ' + paging_request.get_paging_size() + ' rows only'

    def sql_select_now(self):
        return "SELECT CURRENT_TIMESTAMP AS NOW_TIMESTAMP"

    def get_timestamp_precision(self):
        return ChronoUnit.MICROS


class SqlServer2008DbDialect(DbDialect):
    @classmethod
    def INSTANCE(cls):
        return SqlServer2008DbDialect()

    def sql_next_sequence_value_select(self, sequence_name):
        return 'exec dbo.' + sequence_name

    def sql_apply_paging(self, sql_select_from_where, sql_order_by, paging_request):
        if paging_request is None or paging_request.__eq__(PagingRequest.ALL()) or paging_request.__eq__(PagingRequest.NONE()):
            return sql_select_from_where + sql_order_by
        return ElSqlConfig.SQL_SERVER_2008().add_paging(
            sql_select_from_where, paging_request.get_first_item(), paging_request.get_paging_size()
        ) + \
            sql_order_by






