from container_sql_fragment import ContainerSqlFragment


class ConditionalSqlFragment(ContainerSqlFragment):

    def __init__(self,
                 variable,
                 match_value):
        super(ContainerSqlFragment, self).__init__()
        if variable is None:
            raise TypeError('must specificy variable')
        if not variable.startswith(':') or len(variable) < 2:
            raise TypeError('argument not a variable')
        self._variable = variable[1:]
        self._match_value = match_value

    def get_variable(self):
        return self._variable

    def get_match_value(self):
        return self._match_value

    def is_match(self, param_source):
        if not param_source.has_value(self._variable):
            return False
        value = param_source.get_value(self._variable)
        if self._match_value is not None:
            try:
                return self._match_value.upper().__eq__(value.name.upper())
            except AttributeError:
                return self._match_value.upper().__eq__(value.upper())
        if isinstance(value, bool):
            return value
        return True

    def ends_with(self, buf, match):
        if len(buf) >= len(match):
            st = buf[len(buf) - len(match):]
        else:
            st = ''
        return st.__eq__(match)

    def __str__(self):
        return self.__class__.__name__ + ':' + self._variable.__str__() + ' ' + self.get_fragments().__str__()


