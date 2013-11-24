from _abcoll import Container


class ParsedSql(object):
    def __init__(self,
                 original_sql):
        self._origninal_sql = original_sql
        self._parameter_names = []
        self._parameter_indexes = []
        self._named_parameter_count = 0
        self._unnamed_parameter_count = 0
        self._total_parameter_count = 0

    def get_original_sql(self):
        return self._origninal_sql

    def add_named_parameter(self, parameter_name, start_index, end_index):
        self._parameter_names.append(parameter_name)
        self._parameter_indexes.append([start_index, end_index])

    def get_parameter_names(self):
        return self._parameter_names

    def get_parameter_indexes(self, parameter_position):
        return self._parameter_indexes[parameter_position]

    def set_named_parameter_count(self, named_parameter_count):
        self._named_parameter_count = named_parameter_count

    def get_named_parameter_count(self):
        return self._named_parameter_count

    def get_unnamed_parameter_count(self):
        return self._unnamed_parameter_count

    def set_unnamed_parameter_count(self, unnamed_parameter_count):
        self._unnamed_parameter_count = unnamed_parameter_count

    def set_total_parameter_count(self, total_parameter_count):
        self._total_parameter_count = total_parameter_count

    def get_total_parameter_count(self):
        return self._total_parameter_count

    def __str__(self):
        return self._origninal_sql


class ParameterHolder(object):
    def __init__(self,
                 parameter_name,
                 start_index,
                 end_index):
        self._parameter_name = parameter_name
        self._start_index = start_index
        self._end_index = end_index

    def get_parameter_name(self):
        return self._parameter_name

    def get_start_index(self):
        return self._start_index

    def get_end_index(self):
        return self._end_index


class NamedParameterUtils(object):
    PARAMETER_SEPARATORS = ['"', '\'', ':', '&', ',', ';', '(', ')', '|', '=', '+', '-', '*', '%', '/', '\\', '<', '>', '^']
    START_SKIP = ["'", "\"", "--", "/*"]
    STOP_SKIP = ["'", "\"", "\n", "*/"]

    @classmethod
    def parse_sql_statement(cls, sql):
        """
        sql: String
        Parse the SQL statement and locate any placeholders or named parameters.
        """
        named_parameters = set()
        sql_to_use = sql
        parameter_list = []
        statement = sql
        named_parameter_count = 0
        unnamed_parameter_count = 0
        total_parameter_count = 0
        escapes = 0
        i = 0
        while i < len(statement):
            skipToPosition = i
            while i < len(statement):
                skipToPosition = cls.skip_comments_and_quotes(statement, i)
                if i == skipToPosition:
                    break
                else:
                    i = skipToPosition
            if i >= len(statement):
                break
            c = statement[i]
            if c == ':' or c == '&':
                j = i + 1
                if j < len(statement) and statement[j] == ':' and c == ':':
                    i = i + 2
                    continue
                parameter = None
                if j < len(statement) and c == ':' and statement[j] == '{':
                    while j < len(statement) and not '}' == statement[j]:
                        j += 1
                        if ':' == statement[j] or '{' == statement[j]:
                            raise Exception("Parameter name contains invalid character '" + \
                                            statement[j] + "' at position " + i.__str__() + \
                                            " in statement " + sql)
                    if j <= len(statement):
                        raise Exception("Non-terminated named parameter declaration at position " + \
                                        i.__str__() + " in statement " + sql)
                    if j - i > 3:
                        parameter = sql[i+2:j]
                        named_parameter_count = cls.add_new_named_parameter(named_parameters, named_parameter_count, parameter)
                        total_parameter_count = cls.add_named_parameter(parameter_list, total_parameter_count, escapes, i, j + 1, parameter)
                    j += 1
                else:
                    while j < len(statement) and not cls.is_parameter_separator(statement[j]):
                        j += 1
                    if j - i > 1:
                        parameter = sql[i+1:j]
                        named_parameter_count = cls.add_new_named_parameter(named_parameters, named_parameter_count, parameter)
                        total_parameter_count = cls.add_named_parameter(parameter_list, total_parameter_count, escapes, i, j, parameter)
                i = j - 1
            else:
                if c == '\\':
                    j = i + 1
                    if j < len(statement) and statement[j] == ':':
                        sql_to_use = sql_to_use[0: i - escapes] + sql_to_use[i - escapes + 1:]
                        escapes += 1
                        i = i + 2
                        continue
                if c == '?':
                    unnamed_parameter_count += 1
                    total_parameter_count += 1
            i += 1
        parsed_sql = ParsedSql(sql_to_use)
        for ph in parameter_list:
            parsed_sql.add_named_parameter(ph.get_parameter_name(), ph.get_start_index(), ph.get_end_index())
        parsed_sql.set_named_parameter_count(named_parameter_count)
        parsed_sql.set_unnamed_parameter_count(unnamed_parameter_count)
        parsed_sql.set_total_parameter_count(total_parameter_count)
        return parsed_sql


    @classmethod
    def is_parameter_separator(cls, c):
        if c == ' ':
            return True
        for separator in cls.PARAMETER_SEPARATORS:
            if c == separator:
                return True
        return False

    @classmethod
    def add_new_named_parameter(cls, named_parameters, named_parameter_count, parameter):
        if not parameter in named_parameters:
            named_parameters.add(parameter)
            named_parameter_count += 1
        return named_parameter_count

    @classmethod
    def add_named_parameter(cls, parameter_list, total_parameter_count, escapes, i, j, parameter):
        parameter_list.append(ParameterHolder(parameter, i - escapes, j - escapes))
        total_parameter_count += 1
        return total_parameter_count

    @classmethod
    def skip_comments_and_quotes(cls, statement, position):
        for i in xrange(len(cls.START_SKIP)):
            if statement[position] == cls.START_SKIP[i]:
                match = True
                for j in xrange(len(cls.START_SKIP[i])):
                    if not statement[position + j] == cls.START_SKIP[i][j]:
                        match = False
                        break
                if match:
                    offset = len(cls.START_SKIP[i])
                    for m in xrange(position + offset, len(statement)):
                        if statement[m] == cls.STOP_SKIP[i]:
                            end_match = True
                            end_pos = m
                            for n in xrange(1, len(cls.STOP_SKIP[i])):
                                if m + n >= len(statement):
                                    return len(statement)
                                if not statement[m + n] == cls.STOP_SKIP[i][n]:
                                    end_match = False
                                    break
                                end_pos = m + n
                            if end_match:
                                return end_pos + 1
                    return len(statement)
        return position

    @classmethod
    def substitute_named_parameters(cls, parsed_sql, param_source):
        original_sql = parsed_sql.get_original_sql()
        actual_sql = ''
        param_names = parsed_sql.get_parameter_names()
        last_index = 0
        for i in range(len(param_names)):
            param_name = param_names[i]
            indexes = parsed_sql.get_parameter_indexes(i)
            start_index = indexes[0]
            end_index = indexes[1]
            actual_sql += original_sql[last_index:start_index]
            if param_source is not None and param_source.has_value(param_name):
                value = param_source.get_value(param_name)
                if isinstance(value, Container) and not isinstance(value, basestring):
                    k = 0
                    for entry_iter in value:
                        if k > 0:
                            actual_sql += ', '
                            k += 1
                            entry_item = entry_iter
                            if isinstance(entry_item, list):
                                actual_sql += '('
                                for m in xrange(len(entry_item)):
                                    if m > 0:
                                        actual_sql += ', '
                                    actual_sql += '? '
                                actual_sql += ') '
                            else:
                                actual_sql += '? '
                else:
                    actual_sql += '? '
            else:
                actual_sql += '? '
            last_index = end_index
        actual_sql += original_sql[last_index:]
        return actual_sql

    @classmethod
    def build_value_array(cls, parsed_sql, param_source, declared_params=None):
        """
        Convert a Map of named parameter values to a corresponding array.

        """
        param_array = []
        if parsed_sql.get_named_parameter_count() > 0 and parsed_sql.get_unnamed_parameter_count() > 0:
            raise Exception("You can't mix named and traditional ? placeholders.")
        param_names = parsed_sql.get_parameter_names()
        for i in xrange(len(param_names)):
            param_name = param_names[i]
            try:
                value = param_source.get_value(param_name)
                param_array.append(value)
            except Exception, e:
                raise Exception("No value supplied for the SQL parameter '" + param_name + "': " + e.message)
        return param_array


