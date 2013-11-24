

class SqlParameter(object):
    """
    Object to represent a SQL parameter definition.
    <p>Parameters may be anonymous, in which case "name" is {@code null}.
    However, all parameters must define a SQL type according to {@link java.sql.Types}.

    """
    def __init__(self,
                 sql_type=None,
                 type_name=None,
                 scale=None,
                 name=None,
                 other_param=None):
        """
        name: The name of the parameter, if any
        sql_type: SQL type constant from {@code java.sql.Types}
        type_name: Used for types that are user-named like: STRUCT, DISTINCT, JAVA_OBJECT, named array types
        scale: The scale to apply in case of a NUMERIC or DECIMAL type, if any
        """
        self._name = None
        self._sql_type = None
        self._type_name = None
        self._scale = None
        if other_param:
            self._name = other_param._name
            self._sql_type = other_param._sql_type
            self._type_name = other_param._type_name
            self._scale = other_param._scale
        else:
            self._name = name
            self._sql_type = sql_type
            self._type_name = type_name
            self._scale = scale

    def get_name(self):
        """
        Return the name of the parameter.
        """
        return self._name

    def get_sql_type(self):
        """
        Return the SQL type of the parameter.
        """
        return self._sql_type

    def get_scale(self):
        """

        """
        return self._scale

    def get_type_name(self):
        """
        Return the type name of the parameter, if any.
        """
        return self._name

    def is_input_value_provided(self):
        """
        Return whether this parameter holds input values that should be set
        """
        return True

    def is_results_parameter(self):
        """
        Return whether this parameter is an implicit return parameter used during the
        results preocessing of the CallableStatement.getMoreResults/getUpdateCount.
        """
        return False

    @classmethod
    def sql_types_to_anonymous_parameter_list(cls, types):
        """
        Convert a list of ODBC types, as defined in {@code java.sql.Types},
        """
        result = []
        if types is not None:
            for _type in types:
                result.append(SqlParameter(sql_type=_type))
        return result


class SqlParameterValue(SqlParameter):
    """
    Object to represent a SQL parameter value, including parameter metadata
    such as the SQL type and the scale for numeric values.
    <p>Designed for use with {@link JdbcTemplate}'s operations that take an array of
    argument values: Each such argument value may be a {@code SqlParameterValue},
    indicating the SQL type (and optionally the scale) instead of letting the
    template guess a default type. Note that this only applies to the operations with
    a 'plain' argument array, not to the overloaded variants with an explicit type array.

    """
    def __init__(self,
                 sql_type=None,
                 value=None,
                 type_name=None,
                 scale=None,
                 name=None,
                 declared_param=None):
        super(SqlParameterValue, self).__init__(sql_type,
                                                type_name,
                                                scale,
                                                name,
                                                declared_param)
        self._value = value

    def get_value(self):
        """
        Return the value object that this parameter value holds.
        """
        return self._value
