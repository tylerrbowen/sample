from sql_fragment import SqlFragment

class IncludeSqlFragment(SqlFragment):

    def __init__(self,
                 include_key):
        super(IncludeSqlFragment, self).__init__()
        self._include_key = include_key

    def get_include_key(self):
        return self._include_key

    def to_sql(self, buf, bundle, param_source):
        if self._include_key.startswith(':'):
            value = param_source.get_value(self._include_key[1:])
            buf += value + ' '
        else:
            unit = bundle.get_fragment(self._include_key)
            unit.to_sql(buf, bundle, param_source)

    def __str__(self):
        return self.__class__.__name__ + ':' + self._include_key



