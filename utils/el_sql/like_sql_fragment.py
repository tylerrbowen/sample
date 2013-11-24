from container_sql_fragment import ContainerSqlFragment
import re


class LikeSqlFragment(ContainerSqlFragment):

    def __init__(self, variable):
        super(LikeSqlFragment, self).__init__()
        self._variable = variable[1:]

    def get_variable(self):
        return self._variable

    def to_sql(self, buf, bundle, param_source):
        val = param_source.get_value(self._variable)
        value = '' if val is None else val.__str__()
        if bundle.get_config().is_like_wildcard(value):
            buf += 'LIKE '
            super(LikeSqlFragment, self).to_sql(buf, bundle, param_source)
            buf += bundle.get_config().get_like_suffix()
        else:
            buf += '= '
            super(LikeSqlFragment, self).to_sql(buf, bundle, param_source)

    def __str__(self):
        return self.__class__.__name__ + ':' + self._variable.__str__() + ' ' + self.get_fragments().__str__()



class WhereSqlFragment(ContainerSqlFragment):
    def __init__(self):
        super(WhereSqlFragment, self).__init__()
        return

    def to_sql(self, buf, bundle, param_source):
        old_len = len(buf)
        buf += 'WHERE '
        new_len = len(buf)
        super(WhereSqlFragment, self).to_sql(buf, bundle, param_source)
        if len(buf) == new_len:
            #buf = buf[:old_len]
            buf._buf = buf[:old_len]

    def __str__(self):
        return self.__class__.__name__ + ' ' + self.get_fragments()



class PagingSqlFragment(ContainerSqlFragment):

    def __init__(self, offset_variable, fetch_variable):
        super(PagingSqlFragment, self).__init__()
        self._offset_variable = offset_variable
        self._fetch_variable = fetch_variable

    def to_sql(self, buf, bundle, param_source):
        old_len = len(buf)
        super(PagingSqlFragment, self).to_sql(buf, bundle, param_source)
        new_len = len(buf)
        select = buf[old_len:new_len]
        if select.startswith('SELECT '):
            buf._buf = buf[:old_len]
            buf += self.apply_paging(select, bundle, param_source)

    def apply_paging(self, select_to_page, bundle, param_source):
        offset = 0
        fetch_limit = 0
        if self._offset_variable is not None and param_source.has_value(self._offset_variable):
            offset = param_source.get_value(self._offset_variable)
        if param_source.has_value(self._fetch_variable):
            fetch_limit = param_source.get_value(self._fetch_variable)
        elif re.match('[0:9]+', self._fetch_variable) is not None:
        #elif self._fetch_variable.match('[0:9]+') is not None:
            fetch_limit = int(self._fetch_variable)
        return bundle.get_config().add_paging(select_to_page, offset, fetch_limit)

    def __str__(self):
        return self.__class__.__name__ + ' ' + self.get_fragments().__str__()



class OffsetFetchSqlFragment(ContainerSqlFragment):

    def __init__(self, fetch_variable, offset_variable=None):
        super(OffsetFetchSqlFragment, self).__init__()
        self._offset_variable = offset_variable
        self._fetch_variable = fetch_variable

    def to_sql(self, buf, bundle, param_source):
        offset = 0
        fetch_limit = 0
        if self._offset_variable is not None and param_source.has_value(self._offset_variable):
            offset = param_source.get_value(self._offset_variable)
        if param_source.has_value(self._fetch_variable):
            fetch_limit = param_source.get_value(self._fetch_variable)
        elif self._fetch_variable.match('[0:9]+') is not None:
            fetch_limit = int(self._fetch_variable)
        buf += bundle.get_config().get_paging(offset, fetch_limit == fetch_limit)

    def __str__(self):
        return self.__class__.__name__ + ' ' + self._fragments.__str__()