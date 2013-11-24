from db_connector import DbConnector
from db.db_dialect import SqlServer2008DbDialect
from db.template.named_parameter_odbc_template import NamedParameterODBCTemplate
from db.template.transaction.data_source_transaction_manager import DataSourceTransactionManager
from db.template.transaction.transaction_template import TransactionTemplate
from db.template.transaction.default_transaction_defintion import DefaultTransactionDefinition


class DbConnectorFactory(object):

    def __init__(self, base=None):
        self._name = None
        self._data_source = None
        self._database_dialect_class = None
        self._database_dialect = None
        self._mapping_configurations = []
        self._session_factory = None
        self._mapping_resources = []
        self._sqlalchemy_show_sql = False
        self._sqlalchemy_thread_bound = False
        self._sqlalchemy_session_factory = None
        self._transaction_level_name = None
        self._transaction_propagation_behavior_name = None
        self._transaction_timeout_secs = None
        self._transaction_manager = None
        if base is not None:
            self.set_name(base.get_name())
            self.set_dialect(base.get_dialect())
            self.set_datasource(base.get_data_source())
            self.set_sqlalchemy_session_factory(base.get_sqlalchemy_session_factory())
            self.set_transaction_manager(base.get_transaction_manager())

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def set_dialect(self, dialect):
        self._database_dialect = dialect

    def get_dialect(self):
        return self._database_dialect

    def set_datasource(self, datasource):
        self._data_source = datasource

    def get_data_source(self):
        return self._data_source

    def set_sqlalchemy_session_factory(self, sf):
        self._sqlalchemy_session_factory = sf

    def get_sqlalchemy_session_factory(self):
        return self._sqlalchemy_session_factory

    def set_transaction_manager(self, tm):
        self._transaction_manager = tm

    def get_transaction_manager(self):
        return self._transaction_manager

    def get_mapping_files(self):
        return self._mapping_configurations

    def set_mapping_files(self, mapping_configs):
        self._mapping_configurations = mapping_configs

    def get_transaction_propagation_behavior_name(self):
        return self._transaction_propagation_behavior_name

    def set_transaction_propagation_behavior_name(self, n):
        self._transaction_propagation_behavior_name = n

    def get_transaction_level_name(self):
        return self._transaction_level_name

    def set_transaction_level_name(self, n):
        self._transaction_level_name = n

    def get_dialect_name(self):
        return self._database_dialect_class

    def set_dialect_name(self, n):
        self._database_dialect_class = n

    def create_object(self):
        dialect = self.create_dialect()
        odbc_template = self.create_named_parameter_odbc_template()
        sa_factory = None
        sa_template = None
        transaction_template = self.create_transaction_template()
        return DbConnector(self.get_name(), dialect, self.get_data_source(), odbc_template, transaction_template)

    def create_dialect(self):
        dialect = SqlServer2008DbDialect.INSTANCE()
        return dialect

    def create_transaction_definition(self):
        default_trn_def = DefaultTransactionDefinition()
        default_trn_def.set_name(self._name)
        return default_trn_def

    def create_named_parameter_odbc_template(self):
        odbc_template = NamedParameterODBCTemplate(self._data_source)
        return odbc_template

    def create_transaction_manager(self):
        transaction_manager = DataSourceTransactionManager(self._data_source)
        transaction_manager.set_nested_transaction_allowed(True)
        return transaction_manager

    def create_transaction_template(self):
        transaction_manager = self.create_transaction_manager()
        default_trn_def = self.create_transaction_definition()
        transaction_template = TransactionTemplate(transaction_manager=transaction_manager,
                                                   transaction_definition=default_trn_def)
        return transaction_template

