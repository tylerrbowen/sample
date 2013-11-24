import unittest
from utils.bp.instant import Instant
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from db.historical_master.db_historical_time_series_master import DbHistoricalTimeSeriesMaster
from hts.manageable_historical_time_series_info import ManageableHistoricalTimeSeriesInfo
from hts.historical_time_series_info_document import HistoricalTimeSeriesInfoDocument

from db.date_utils import DbDateUtils
from db.sql_data_source import MSSQLDataSource
from ids.object_id import UniqueId
from ids.external_id_bundle_with_dates import ExternalIdBundleWithDates, ExternalIdWithDates
from utils.bp.local_date import LocalDate
from ids.external_id_bundle import ExternalIdBundle, ExternalId
from db.db_connector_factory import DbConnectorFactory


class AbstractDbHTSMasterTest(unittest.TestCase):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server} server=(local) database=PORTFOLIO_MANAGEMENT_DB'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()
        self._now = None
        self._version_1_instant = None
        self._version_2_instant = None
        self._version_3_instant = None
        self._version_4_instant = None
        self._totalHistoricalTimeSeries = 0

    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def init_db_connector(self):
        self.data_source = self.get_data_source()
        dbconnector_factory = DbConnectorFactory()
        dbconnector_factory.set_name(self.name)
        dbconnector_factory.set_datasource(self.data_source)
        self.db_connector = dbconnector_factory.create_object()

    def get_data_source(self):
        data_source = MSSQLDataSource(self.connection_string)
        return data_source

    def doSetUp(self):
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self._now = Instant.now_clock(self.hts_master.get_clock())
        self._version_1_instant = self._now.minus_seconds(100)
        self._version_2_instant = self._now.minus_seconds(50)
        self._version_3_instant = self._now.minus_seconds(40)
        self._version_4_instant = self._now.minus_seconds(30)
        template = self.hts_master.get_db_connector().get_operations()
        template.update(("INSERT INTO hts_name VALUES (?,?)",(
        1, "N101")))
        template.update(("INSERT INTO hts_name VALUES (?,?)",(
        2, "N102")))
        template.update(("INSERT INTO hts_name VALUES (?,?)",(
            3, "N201")))
        template.update(("INSERT INTO hts_name VALUES (?,?)",(
            4, "N202")))
        template.update(("INSERT INTO hts_name VALUES (?,?)",(
            5, "N203")))
        template.update(("INSERT INTO hts_data_field VALUES (?,?)",(
            11, "DF11")))
        template.update(("INSERT INTO hts_data_field VALUES (?,?)",(
            12, "DF12")))
        template.update(("INSERT INTO hts_data_source VALUES (?,?)",(
            21, "DS21")))
        template.update(("INSERT INTO hts_data_source VALUES (?,?)",(
            22, "DS22")))
        template.update(("INSERT INTO hts_data_provider VALUES (?,?)",(
            31, "DP31")))
        template.update(("INSERT INTO hts_data_provider VALUES (?,?)",(
            32, "DP32")))
        template.update(("INSERT INTO hts_observation_time VALUES (?,?)",(
            41, "OT41")))
        template.update(("INSERT INTO hts_observation_time VALUES (?,?)",(
            42, "OT42")))
        template.update(("INSERT INTO hts_document VALUES (?,?,?,?,?, ?,?,?,?,?, ?)",(
            101, 101,
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP,
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP, 1, 11, 21, 31, 41)))
        template.update(("INSERT INTO hts_document VALUES (?,?,?,?,?, ?,?,?,?,?, ?)",(
            102, 102,
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP,
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP, 2, 12, 22, 32, 42)))
        template.update(("INSERT INTO hts_document VALUES (?,?,?,?,?, ?,?,?,?,?, ?)",(
            201, 201,
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP, 3, 11, 21, 31, 41)))
        template.update(("INSERT INTO hts_document VALUES (?,?,?,?,?, ?,?,?,?,?, ?)",(
            202, 201,
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP,
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_3_instant), 4, 11, 21, 31, 42)))
        template.update(("INSERT INTO hts_document VALUES (?,?,?,?,?, ?,?,?,?,?, ?)",(
            203, 201, DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP,
            DbDateUtils.to_sql_timestamp(self._version_3_instant),
            DbDateUtils.MAX_SQL_TIMESTAMP, 5, 11, 21, 31, 42)))
        self._totalHistoricalTimeSeries = 3

        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            501, "TICKER", "V501")))
        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            502, "NASDAQ", "V502")))
        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            503, "TICKER", "V503")))
        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            504, "NASDAQ", "V504")))
        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            505, "TICKER", "V505")))
        template.update(("INSERT INTO hts_idkey VALUES (?,?,?)",(
            506, "NASDAQ", "V506")))

        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            1, 101, 501, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            2, 101, 502, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            3, 102, 503, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            4, 102, 504, DbDateUtils.to_sql_date(LocalDate.of(2011, 6, 30)), DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            5, 201, 505, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            6, 201, 506, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            7, 202, 505, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            8, 202, 506, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            9, 203, 505, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))
        template.update(("INSERT INTO hts_doc2idkey (id, doc_id, idkey_id, valid_from, valid_to) VALUES (?,?,?,?,?)",(
            10, 203, 506, DbDateUtils.MIN_SQL_DATE, DbDateUtils.MAX_SQL_DATE)))

        template.update(("INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101, DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 1)),
            DbDateUtils.to_sql_timestamp(self._version_1_instant),
            DbDateUtils.to_sql_timestamp(self._version_1_instant), 3.1)))
        template.update(("INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101, DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 2)),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_2_instant), 3.2)))
        template.update(("INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101, DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 3)),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_2_instant), 3.3)))
        template.update(("INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101, DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 2)),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_3_instant), 3.21)))
        template.update(("INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101, DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 2)),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_4_instant), 3.22)))
        template.update((
            "INSERT INTO hts_point VALUES (?,?,?,?,?)",(
            101,
            DbDateUtils.to_sql_date(LocalDate.of(2011, 1, 3)),
            DbDateUtils.to_sql_timestamp(self._version_2_instant),
            DbDateUtils.to_sql_timestamp(self._version_4_instant), 3.33)))


    def assert101(self, test):
        uniqueId = UniqueId.of(scheme="DbHts", value="101", version="0")
        self.assertIsNotNone(test)
        self.assertEquals(uniqueId, test.get_unique_id())
        self.assertEquals(self._version_1_instant, test.get_version_from_instant())
        self.assertEquals(None, test.get_version_to_instant())
        self.assertEquals(self._version_1_instant, test.get_correction_from_instant())
        self.assertEquals(None, test.get_correction_to_instant())
        info = test.get_info()
        self.assertIsNotNone(info)
        self.assertEquals(uniqueId, info.get_unique_id())
        self.assertEquals("N101", info.get_name())
        self.assertEquals("DF11", info.get_data_field())
        self.assertEquals("DS21", info.get_data_source())
        self.assertEquals("DP31", info.get_data_provider())
        self.assertEquals("OT41", info.get_observation_time())
        key = info.get_external_id_bundle()
        self.assertIsNotNone(key)
        self.assertEquals(2, key.size())
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("TICKER", "V501"), None, None)))
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("NASDAQ", "V502"), None, None)))
        

    def assert102(self, test):
        uniqueId = UniqueId.of(scheme="DbHts", value="102", version="0")
        self.assertIsNotNone(test)
        self.assertEquals(uniqueId, test.get_unique_id())
        self.assertEquals(self._version_1_instant, test.get_version_from_instant())
        self.assertEquals(None, test.get_version_to_instant())
        self.assertEquals(self._version_1_instant, test.get_correction_from_instant())
        self.assertEquals(None, test.get_correction_to_instant())
        info = test.get_info()
        self.assertIsNotNone(info)
        self.assertEquals(uniqueId, info.get_unique_id())
        self.assertEquals("N102", info.get_name())
        self.assertEquals("DF12", info.get_data_field())
        self.assertEquals("DS22", info.get_data_source())
        self.assertEquals("DP32", info.get_data_provider())
        self.assertEquals("OT42", info.get_observation_time())
        key = info.get_external_id_bundle()
        self.assertIsNotNone(key)
        self.assertEquals(2, key.size())
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("TICKER", "V503"), None, None)))
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("NASDAQ", "V504"), LocalDate.of(2011, 6, 30), None)))
        

    def assert201(self, test):
        uniqueId = UniqueId.of(scheme="DbHts",  value="201", version="0")
        self.assertIsNotNone(test)
        self.assertEquals(uniqueId, test.get_unique_id())
        self.assertEquals(self._version_1_instant, test.get_version_from_instant())
        self.assertEquals(self._version_2_instant, test.get_version_to_instant())
        self.assertEquals(self._version_1_instant, test.get_correction_from_instant())
        self.assertEquals(None, test.get_correction_to_instant())
        info = test.get_info()
        self.assertIsNotNone(info)
        self.assertEquals(uniqueId, info.get_unique_id())
        self.assertEquals("N201", info.get_name())
        self.assertEquals("DF11", info.get_data_field())
        self.assertEquals("DS21", info.get_data_source())
        self.assertEquals("DP31", info.get_data_provider())
        self.assertEquals("OT41", info.get_observation_time())
        key = info.get_external_id_bundle()
        self.assertIsNotNone(key)
        self.assertEquals(2, key.size())
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("TICKER", "V505"), None, None)))
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("NASDAQ", "V506"), None, None)))
        

    def assert202(self, test):
        uniqueId = UniqueId.of(scheme="DbHts",  value="201", version="1")
        self.assertIsNotNone(test)
        self.assertEquals(uniqueId, test.get_unique_id())
        self.assertEquals(self._version_2_instant, test.get_version_from_instant())
        self.assertEquals(None, test.get_version_to_instant())
        self.assertEquals(self._version_2_instant, test.get_correction_from_instant())
        self.assertEquals(self._version_3_instant, test.get_correction_to_instant())
        info = test.get_info()
        self.assertIsNotNone(info)
        self.assertEquals(uniqueId, info.get_unique_id())
        self.assertEquals("N202", info.get_name())
        self.assertEquals("DF11", info.get_data_field())
        self.assertEquals("DS21", info.get_data_source())
        self.assertEquals("DP31", info.get_data_provider())
        self.assertEquals("OT42", info.get_observation_time())
        key = info.get_external_id_bundle()
        self.assertIsNotNone(key)
        self.assertEquals(2, key.size())
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("TICKER", "V505"), None, None)))
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("NASDAQ", "V506"), None, None)))

    def assert203(self, test):
        uniqueId = UniqueId.of(scheme="DbHts",value= "201", version="2")
        self.assertIsNotNone(test)
        self.assertEquals(uniqueId, test.get_unique_id())
        self.assertEquals(self._version_2_instant, test.get_version_from_instant())
        self.assertEquals(None, test.get_version_to_instant())
        self.assertEquals(self._version_3_instant, test.get_correction_from_instant())
        self.assertEquals(None, test.get_correction_to_instant())
        info = test.get_info()
        self.assertIsNotNone(info)
        self.assertEquals(uniqueId, info.get_unique_id())
        self.assertEquals("N203", info.get_name())
        self.assertEquals("DF11", info.get_data_field())
        self.assertEquals("DS21", info.get_data_source())
        self.assertEquals("DP31", info.get_data_provider())
        self.assertEquals("OT42", info.get_observation_time())
        key = info.get_external_id_bundle()
        self.assertIsNotNone(key)
        self.assertEquals(2, key.size())
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("TICKER", "V505"), None, None)))
        self.assertEquals(True, key.get_external_ids().contains(
            ExternalIdWithDates.of(ExternalId.of("NASDAQ", "V506"), None, None)))


