

from conditional_sql_fragment import ConditionalSqlFragment


class AndSqlFragment(ConditionalSqlFragment):

    def __init__(self,
                 variable,
                 match_value):
        super(AndSqlFragment, self).__init__(variable, match_value)
        self._fragments = []

    def to_sql(self, buf, bundle, param_source):
        if self.is_match(param_source):
            if not self.ends_with(buf, ' WHERE ') and not self.ends_with(buf, ' AND '):
                buf += 'AND '
            super(AndSqlFragment, self).to_sql(buf, bundle, param_source)



class OrSqlFragment(ConditionalSqlFragment):
    def __init__(self,
                 variable,
                 match_value):
        super(OrSqlFragment, self).__init__(variable, match_value)
        self._fragments = []

    def to_sql(self, buf, bundle, param_source):
        if self.is_match(param_source):
            if not self.ends_with(buf, ' WHERE ') and not self.ends_with(buf, ' OR '):
                buf += 'OR '
            super(OrSqlFragment, self).to_sql(buf, bundle, param_source)


