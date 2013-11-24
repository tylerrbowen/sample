
import unittest
from utils.bp.instant import Instant
import datetime
import pytz
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from db.security.db_security_master import DbSecurityMaster
from db.db_connector import DbConnector
from db.sql_data_source import MSSQLDataSource
from db.db_dialect import SqlServer2008DbDialect
from db.template.odbc_template import ODBCTemplate
from db.template.named_parameter_odbc_template import NamedParameterODBCTemplate
from db.template.transaction.transaction_template import TransactionTemplate
from db.template.transaction.default_transaction_defintion import DefaultTransactionDefinition
from db.template.transaction.data_source_transaction_manager import DataSourceTransactionManager
from security.manageable.security_document import SecurityDocument
from financial.security.equity.equity_security import EquitySecurity
from financial.security.equity.gics_code import GICSCode
from currency.currency_base import Currency
from ids.external_id_bundle import ExternalIdBundle
from db.db_connector_factory import DbConnectorFactory


class TestDbSecurityMaster(unittest.TestCase):
    def setUp(self):
        self.name = 'TestSecMaster'
        self.connection_string = 'driver={sql server}; server=(local); database=PORTFOLIO_MANAGEMENT_DB;'
        self.db_connector = None
        self.dialect = None
        self.odbc_template = None
        self.transaction_template = None
        self.init_db_connector()
        self.sec_master = DbSecurityMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None
        self.sec_master = None

    def init_db_connector(self):
        self.data_source = self.get_data_source()
        dbconnector_factory = DbConnectorFactory()
        dbconnector_factory.set_name(self.name)
        dbconnector_factory.set_datasource(self.data_source)
        self.db_connector = dbconnector_factory.create_object()
        # self.data_source = self.get_data_source()
        # self.dialect = self.get_dialect()
        # self.odbc_template = self.get_odbc_template()
        # self.transaction_template = self.get_transaction_template()
        # self.db_connector = DbConnector(self.name,
        #                                 self.dialect,
        #                                 self.data_source,
        #                                 self.odbc_template,
        #                                 self.transaction_template)

    def get_data_source(self):
        data_source = MSSQLDataSource(self.connection_string)
        return data_source

    def get_dialect(self):
        dialect = SqlServer2008DbDialect.INSTANCE()
        return dialect

    def get_odbc_template(self):
        odbc_template = NamedParameterODBCTemplate(self.data_source)#ODBCTemplate(self.data_source)
        return odbc_template

    def get_default_trn_def(self):
        default_trn_def = DefaultTransactionDefinition()
        default_trn_def.set_name(self.name)
        return default_trn_def

    def get_transaction_manager(self):
        transaction_manager = DataSourceTransactionManager(self.data_source)
        transaction_manager.set_nested_transaction_allowed(True)

        return transaction_manager

    def get_transaction_template(self):
        transaction_manager = self.get_transaction_manager()
        default_trn_def = self.get_default_trn_def()
        transaction_template = TransactionTemplate(transaction_manager=transaction_manager,
                                                   transaction_definition=default_trn_def)
        return transaction_template

    def test_basics(self):
        self.assertIsNotNone(self.sec_master)
        self.assertEquals(True, self.sec_master.get_unique_id_scheme().__eq__('DbSec'))
        self.assertIsNotNone(self.sec_master.get_db_connector())
        self.assertIsNotNone(self.sec_master.get_clock())

    def test_equity(self):
        sec = EquitySecurity('London', 'LON', 'OpenGamma Ltd', Currency.USD())
        sec.set_name('OpenGamma')
        sec.set_gics_code(GICSCode.of('20102010'))
        sec.set_short_name('OG')
        sec.set_external_id_bundle(ExternalIdBundle.of('Test', 'OG'))
        add_doc = SecurityDocument(sec)
        added = self.sec_master.add(add_doc)
        loaded = self.sec_master.get(unique_id=added.get_unique_id())
        self.assertEquals(added, loaded)

    def test_to_string(self):
        self.assertEquals('DbSecurityMaster[DbSec]', self.sec_master.__str__())


def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestDbSecurityMaster)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()



