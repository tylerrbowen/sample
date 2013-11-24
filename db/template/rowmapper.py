from abc import ABCMeta, abstractmethod


class RowMapper(object):
    """
    An interface used by {@link JdbcTemplate} for mapping rows of a
    {@link java.sql.ResultSet} on a per-row basis. Implementations of this
    interface perform the actual work of mapping each row to a result object,
    but don't need to worry about exception handling.
    {@link java.sql.SQLException SQLExceptions} will be caught and handled
    by the calling JdbcTemplate.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def map_row(self, rs, row_num):
        pass


class SingleColumnRowMapper(RowMapper):
    """
    {@link RowMapper} implementation that converts a single column into a single
    result value per row. Expects to operate on a {@code java.sql.ResultSet}
    that just contains a single column.
    <p>The type of the result value for each row can be specified. The value
    for the single column will be extracted from the {@code ResultSet}
    and converted into the specified target type.
    """
    def __init__(self,
                 required_type=None):
        self._required_type = required_type

    def get_required_type(self):
        return self._required_type

    def set_required_type(self, required_type):
        self._required_type = required_type

    def map_row(self, rs, row_num):
        """
        Extract a value for the single column in the current row.
        <p>Validates that there is only one column selected,
        then delegates to {@code getColumnValue()} and also
        {@code convertValueToRequiredType}, if necessary.

        """
        nr_of_columns = len(rs)
        if nr_of_columns != 1:
            raise IncorrectResultSetColumnCountException(expected_count=1,
                                                         actual_count=nr_of_columns)
        result = self.get_column_value(rs, 0)
        if result is not None and self._required_type is not None and not isinstance(result, self._required_type):
            try:
                return self.convert_value_to_required_type(result, self._required_type)
            except TypeError, e:
                raise TypeError(
                    "Type mismatch affecting row number " + row_num.__str__() + " and column type '" + \
						rs.cursor_description[0][1].__name__ + "': " + e.message)
        return result

    def convert_value_to_required_type(self, value, required_type):
        raise NotImplementedError()

    def get_column_value(self, rs, index):
        return rs[index]


class ColumnMapRowMapper(RowMapper):

    def map_row(self, rs, row_num):
        try:
            rs_meta_data = rs.cursor_description
        except (IndexError, AttributeError), e:
            raise Exception(e)
        column_count = len(rs_meta_data)
        map_of_col_values = self.create_column_map(column_count)
        for i in range(column_count):
            key = self.get_column_key(rs_meta_data[i][0])
            obj = self.get_column_value(rs, i)
            map_of_col_values[key] = obj
        return map_of_col_values

    def create_column_map(self, column_count):
        return dict()

    def get_column_key(self, column_name):
        return column_name

    def get_column_value(self, rs, index):
        return rs[index]



class IncorrectResultSetColumnCountException(Exception):

    def __init__(self,
                 expected_count,
                 actual_count):
        super(IncorrectResultSetColumnCountException, self).__init__(
            "Incorrect column count: expected " + expected_count.__str__() + ", actual " + actual_count.__str__()
        )
        self._expected_count = expected_count
        self._actual_count = actual_count
        self.message = "Incorrect column count: expected " + expected_count.__str__() + ", actual " + actual_count.__str__()





