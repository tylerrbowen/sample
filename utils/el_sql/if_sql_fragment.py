from conditional_sql_fragment import ConditionalSqlFragment


class IfSqlFragment(ConditionalSqlFragment):

    def __init__(self,
                 variable,
                 match_value):
        ConditionalSqlFragment.__init__(self, variable, match_value)
        self._fragments = []

    def to_sql(self, buf, bundle, param_source):
        if self.is_match(param_source):
            super(IfSqlFragment, self).to_sql(buf, bundle, param_source)

