from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource


class NamedDimensionDbTable(object):
    """
     A dimension table within a star schema.
     <p>
     This class aims to simplify working with a simple dimension table.
     This kind of table consists of simple deduplicated data, keyed by id.
     The id is used to reference the data on the main "fact" table.
     <p>
     This class uses SQL via JDBC. The SQL may be changed by subclassing the relevant methods.
    """

    def __init__(self, db_connector, variable_name, table_name, sequence_name):
        """
        Creates an instance.
        
        @param dbConnector  the database connector combining all configuration, not null
        @param variableName  the variable name, used as a placeholder in SQL, not null
        @param tableName  the table name, not null
        @param sequence_name  the sequence used to generate the id, may be null
    
        _dbConnector: DbConnector: The database connector.
        _variableName: String: The variable name.
        _tableName: String: The table name.
        _sequenceName: String: The sequence used to generate the id.
        """
        self._db_connector = db_connector
        self._variable_name = variable_name
        self._table_name = table_name
        self._sequence_name = sequence_name
    
    
    def get_db_connector(self):
        """
        Gets the database connector.
        retrns: DbConnector
        """
        return self._db_connector
    
    def get_variable_name(self):
        """
        Gets the variable name.
        returns: String
        """
        return self._variable_name
    
    def get_table_name(self):
        """
        Gets the table name.
        return: String
        """
        return self._table_name
    
    def get_sequence_name(self):
        """
        Gets the sequence name.
        return: String
        """
        return self._sequence_name
    
    def get_dialect(self):
        """
        Gets the database dialect.
        DbDialect
        """
        return self.get_db_connector().get_dialect()
    
    def next_id(self):
        """
        Gets the next database id.
        returns: long
        """
        return self.get_db_connector().get_odbc_template().query_for_list(
            self.get_dialect().sql_next_sequence_value_select(self._sequence_name),
            param_map=None
        )
    
    
    def get(self, name):
        """
        arg: String
        Gets the id for the name matching exactly.
        *
        @param name  the name to lookup, not null
        @return the id, null if not stored
    
        returns: long
        """
        select = self.sql_select_get()
        args = DbMapSqlParameterSource().add_value(self.get_variable_name(), name)
        result = self.get_db_connector().get_odbc_template().query_for_list(select, args, rch=True)
        if len(result) == 1:
            return result[0]["dim_id"]
        return None
    
    
    
    def sql_select_get(self):
        """
        /**
        Gets an SQL select statement suitable for finding the name.
        <p>
        The SQL requires a parameter of name {@link #getVariableName()}.
        The statement returns a single column of the id.
        *
        @return the SQL, not null
        */
        String
        """
        return 'SELECT dim.id AS dim_id ' + \
            'FROM ' + self.get_table_name() + ' dim ' + \
            'WHERE dim.name = :' + self.get_variable_name() + ' '
    
    def search(self, name):
        """
        String
        /**
        Searches for the id for the name matching any case and using wildcards.
        *
        @param name  the name to lookup, not null
        @return the id, null if not stored
        */
        return: Long
        """
        select = self.sql_select_search(name)
        args = DbMapSqlParameterSource().add_value(self.get_variable_name(), self.get_dialect().sql_wildcard_adjust_value(name))
        result = self.get_db_connector().get_odbc_template().query_for_list(select, args, rch=True)
        if len(result)==0:
            return None
        return result[0].get("dim_id")
    
    def sql_select_search(self, name):
        """
        String
        Gets an SQL select statement suitable for finding the name.
        <p>
        The SQL requires a parameter of name {@link #getVariableName()}.
        The statement returns a single column of the id.
        *
        @param name  the name to lookup, not null
        @return the SQL, not null
        String
        """
        return 'SELECT dim.id AS dim_id ' + \
          'FROM ' + self.get_table_name() + ' dim ' + \
          'WHERE ' + self.get_dialect().sql_wildcard_query('UPPER(dim.name) ', 'UPPER(:' + self.get_variable_name() + ')', name)
    
    
    
    def ensure(self, name):
        """
        String
        Gets the id adding it if necessary.
        *
        @param name  the name to ensure is present, not null
        @return the id, null if not stored
        return long
        """
        select = self.sql_select_get()
        args = DbMapSqlParameterSource().add_value(self.get_variable_name(), name)
        result = self.get_db_connector().get_odbc_template().query_for_list(select, args, rch=True)
        if len(result) == 1:
            return result[0].get("dim_id")
    
        id_ = self.next_id()[0]
        args.add_value("dim_id", id_)
        self.get_db_connector().get_odbc_template().update(self.sql_insert(), args)
        return id_
    
    def sql_insert(self):
        """
        Gets an SQL insert statement suitable for finding the name.
        <p>
        The SQL requires a parameter of name {@link #getVariableName()}.
        *
        @return the SQL, not null
        String
        """
        return 'INSERT INTO ' + self.get_table_name() + ' (id, name) ' + \
          'VALUES (:dim_id, :' + self.get_variable_name() + ')'
    
    def names(self):
        """
        Lists all the names in the table, sorted alphabetically.
        *
        @return the set of names, not null
        return: List<String>
        """
        return self.get_db_connector().get_odbc_template().query_for_list(self.sql_select_names())

    
    def sql_select_names(self):
        """
        Gets an SQL list names.
        *
        @return the SQL, not null
        return String
        """
        return 'SELECT name FROM ' + self.get_table_name() + ' ORDER BY name'
    
    def __str__(self):
        return 'Dimension[' + self.get_table_name() + ']'