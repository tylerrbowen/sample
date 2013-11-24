from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty

from sql_parameter_value import SqlParameterValue


class SqlParameterSource(object):
    """
    Interface that defines common functionality for objects that can
    offer parameter values for named SQL parameters, serving as argument
    or {@link NamedParameterODBCTemplate} operations.
    """
    __metaclass__ = ABCMeta

    TYPE_UNKNOWN = -2147483648

    @abstractmethod
    def has_value(self, param_name):
        """
        Determine whether there is a value for the specified named parameter.
        @param paramName the name of the parameter
        @return whether there is a value defined
        """
        return

    @abstractmethod
    def get_value(self, param_name):
        """
        Return the parameter value for the requested named parameter.
        @param paramName the name of the parameter
        @return the value of the specified parameter
        """
        return

    @abstractmethod
    def get_sql_type(self, param_name):
        """
        Determine the SQL type for the specified named parameter.
        @param paramName the name of the parameter
        @return the SQL type of the specified parameter,
        or {@code TYPE_UNKNOWN} if not known
        """
        return

    @abstractmethod
    def get_type_name(self, param_name):
        """
        Determine the type name for the specified named parameter.
        @param paramName the name of the parameter
        @return the type name of the specified parameter,
        or {@code null} if not known
        """
        return


class AbstractSqlParameterSource(SqlParameterSource):
    __metaclass__ = ABCMeta

    @abstractproperty
    def sql_types(self):
        return

    @abstractproperty
    def type_names(self):
        return

    @abstractmethod
    def register_sql_type(self, param_name, sql_type):
        """
        Register a SQL type for the given parameter.
        @param paramName the name of the parameter
        @param sqlType the SQL type of the parameter
        """
        assert param_name is not None
        self.sql_types[param_name] = sql_type

    @abstractmethod
    def register_type_name(self, param_name, type_name):
        """
        Register a SQL type for the given parameter.
        @param paramName the name of the parameter
        @param typeName the type name of the parameter
        """
        assert param_name is not None
        self.type_names[param_name] = type_name

    @abstractmethod
    def get_sql_type(self, param_name):
        """
        Return the SQL type for the given parameter, if registered.
        @param paramName the name of the parameter
        @return the SQL type of the parameter,
        or {@code TYPE_UNKNOWN} if not registered
        """
        assert param_name is not None
        sql_type = self.sql_types.get(param_name)
        if sql_type is not None:
            return sql_type
        return self.TYPE_UNKNOWN

    @abstractmethod
    def has_value(self, param_name):
        return super(AbstractSqlParameterSource, self).has_value(param_name)

    @abstractmethod
    def get_value(self, param_name):
        return super(AbstractSqlParameterSource, self).get_value(param_name)

    @abstractmethod
    def get_type_name(self, param_name):
        assert param_name is not None
        return self.type_names.get(param_name)



class MapSqlParameterSource(AbstractSqlParameterSource):
    """
    {@link SqlParameterSource} implementation that holds a given Map of parameters.
    <p>This class is intended for passing in a simple Map of parameter values
    to the methods of the {@link NamedParameterJdbcTemplate} class.

    <p>The {@code addValue} methods on this class will make adding several
    values easier. The methods return a reference to the {@link MapSqlParameterSource}
    itself, so you can chain several method calls together within a single statement.
    """
    def __init__(self,
                 param_name='',
                 value=None,
                 values=None):
        self._values = dict()
        self._sql_types = dict()
        self._type_names = dict()
        if value is not None:
            self.add_value(param_name, value)
        elif values is not None:
            self.add_values(values)

    @property
    def values(self):
        return self._values

    @property
    def sql_types(self):
        return self._sql_types

    @property
    def type_names(self):
        return self._type_names

    def register_sql_type(self, param_name, sql_type):
        super(MapSqlParameterSource, self).register_sql_type(param_name, sql_type)

    def register_type_name(self, param_name, type_name):
        super(MapSqlParameterSource, self).register_type_name(param_name, type_name)

    def get_sql_type(self, param_name):
        return super(MapSqlParameterSource, self).get_sql_type(param_name)

    def get_type_name(self, param_name):
        return super(MapSqlParameterSource, self).get_type_name(param_name)

    def add_value(self,
                  param_name,
                  value,
                  sql_type=None,
                  type_name=None):
        """
        Add a parameter to this parameter source.
        @param paramName the name of the parameter
        @param value the value of the parameter
        @return a reference to this parameter source,
        so it's possible to chain several calls together
        """
        assert param_name is not None
        self.values[param_name] = value
        if isinstance(value, SqlParameterValue):
            self.register_sql_type(param_name, value.get_sql_type())
            return self
        elif sql_type is not None:
            self.register_sql_type(param_name, sql_type)
            if type_name is not None:
                self.register_type_name(param_name, type_name)
            return self
        else:
            return self

    def add_values(self,
                   values):
        if isinstance(values, MapSqlParameterSource):
            self._values = values._values
        elif isinstance(values, dict):
            for key, value in values.iteritems():
                self.values[key] = value
                if isinstance(value, SqlParameterValue):
                    self.register_sql_type(key, value.get_sql_type())
        return self

    def get_values(self):
        return self.values.values()

    def has_value(self, param_name):
        return param_name in self.values.keys()

    def get_value(self, param_name):
        if not self.has_value(param_name):
            raise TypeError("No value registered for key '" + param_name+ "'")
        return self.values.get(param_name)


