

class ElSqlConfig(object):
    """
    Configuration that provides support for differences between databases.
    The class provides SQL fragments that the tags use to build the complete SQL.
    Some standard implementations have been provided, but subclasses may be added.
    Implementations must be thread-safe.
    """
    @classmethod
    def DEFAULT(cls):
        return ElSqlConfig("Default")

    @classmethod
    def POSTGRES(cls):
        return PostgresElSqlConfig()

    @classmethod
    def HSQL(cls):
        return HsqlElSqlConfig()

    @classmethod
    def MYSQL(cls):
        return MySqlElSqlConfig()

    @classmethod
    def ORACLE(cls):
        pass

    @classmethod
    def SQL_SERVER_2008(cls):
        return SqlServer2008ElSqlConfig();

    def __init__(self,
                 name):
        """
        @param name  a descriptive name for the config, not null
        """
        self._name = name

    def get_name(self):
        return self._name

    def is_like_wildcard(self, value):
        """
        Checks if the value contains a wildcard.
        The default implementation matches % and _, using backslash as an escape character.
        This matches Postgres and other databases.
        @param value  the value to check, not null
        @return true if the value contains wildcards
        """
        escape = False
        for i, v in enumerate(value):
            if escape:
                escape = False
            else:
                if v == '\\':
                    escape = True
                elif v == '%' or v == '_':
                    return True
        return False

    def get_like_suffix(self):
        return ''

    def add_paging(self, select_to_page, offset, fetch_limit):
        """
        Alters the supplied SQL to add paging, such as OFFSET-FETCH.
        The default implementation calls {@link #getPaging(int, int)}.
        The returned SQL must be end in a space if non-empty.
        @param selectToPage  the SELECT statement to page, not null
        @param offset  the OFFSET amount, zero to start from the beginning
        @param fetchLimit  the FETCH/LIMIT amount, zero to fetch all
        @return the updated SELECT, not null
        """
        return select_to_page + self.get_paging(offset, fetch_limit)

    def get_paging(self, offset, fetch_limit):
        """
        Gets the paging SQL, such as OFFSET-FETCH.
        The default implementation uses 'FETCH FIRST n ROWS ONLY' or
        'OFFSET n ROWS FETCH NEXT n ROWS ONLY'.
        This matches Postgres, HSQL and other databases.
        The returned SQL must be end in a space if non-empty.
        @param offset  the OFFSET amount, zero to start from the beginning
        @param fetchLimit  the FETCH/LIMIT amount, zero to fetch all
        @return the SQL to use, not null
        """
        if fetch_limit == 0 and offset == 0:
            return ''
        if fetch_limit == 0:
            return 'OFFSET ' + offset.__str__() + ' ROWS '
        if offset == 0:
            return 'FETCH FIRST ' + fetch_limit.__str__() + ' ROWS ONLY '
        return 'OFFSET ' + offset.__str__() + ' ROWS FETCH NEXT ' + fetch_limit.__str__() + ' ROWS ONLY '

    def __str__(self):
        return 'ElSqlConfig[' + self._name + ']'


class PostgresElSqlConfig(ElSqlConfig):
    def __init__(self):
        super(PostgresElSqlConfig, self).__init__('Postgres')



class HsqlElSqlConfig(ElSqlConfig):
    def __init__(self):
        super(HsqlElSqlConfig, self).__init__('HSQL')

    def get_like_suffix(self):
        return 'ESCAPE \'\\\' '


class MySqlElSqlConfig(ElSqlConfig):
    def __init__(self):
        super(MySqlElSqlConfig, self).__init__('MySql')


    def get_paging(self, offset, fetch_limit):
        if fetch_limit == 0 and offset == 0:
            return ''
        if fetch_limit == 0:
            return 'OFFSET ' + offset.__str__() + ' '
        if offset == 0:
            return 'LIMIT ' + fetch_limit.__str__() + ' '
        return 'LIMIT ' + fetch_limit.__str__() + ' OFFSET ' + offset.__str__() + ' '


class SqlServer2008ElSqlConfig(ElSqlConfig):
    """
    Class for SQL server 2008.
    """
    def __init__(self):
        super(SqlServer2008ElSqlConfig, self).__init__('SqlServer2008')

    def add_paging(self, select_to_page, offset, fetch_limit):
        """
        SQL Server needs a SELECT TOP with ORDER BY in an inner query, otherwise it complains
        """
        if fetch_limit == 0 and offset == 0:
            return select_to_page.replace('SELECT ', 'SELECT TOP ' + 0x7fffffffffffffffL.__str__() + ' ')
        start = offset + 1
        end = offset + fetch_limit
        columns = select_to_page[select_to_page.find('SELECT ') + 7:select_to_page.find(' FROM ')]
        from_ = select_to_page[select_to_page.find(' FROM ') + 6:select_to_page.find(' ORDER BY ')]
        order_ = select_to_page[select_to_page.find(' ORDER BY' ) + 10:]
        inner = 'SELECT ' + columns + ', ROW_NUMBER() OVER (ORDER BY ' + order_.strip() + ') AS ROW_NUM FROM ' + from_
        return 'SELECT * FROM (' + \
               inner + \
               ') AS ROW_TABLE WHERE ROW_NUM >= ' + \
               start.__str__() + ' AND ROW_NUM <= ' + \
               end.__str__()

    def get_paging(self, offset, fetch_limit):
        raise NotImplementedError()

