
import unittest
from abstract_test_db_hts import AbstractDbHTSMasterTest
from og_p_sample.utils.bp.instant import Instant
from utils.argument_checker import IllegalArgumentException
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from db.historical_master.db_historical_time_series_master import DbHistoricalTimeSeriesMaster
from hts.manageable_historical_time_series_info import ManageableHistoricalTimeSeriesInfo
from hts.historical_time_series_info_document import HistoricalTimeSeriesInfoDocument
from hts.historical_time_series_info_history_request import HistoricalTimeSeriesInfoHistoryRequest
from ids.object_id import UniqueId
from ids.external_id_bundle_with_dates import ExternalIdBundleWithDates, ExternalIdWithDates
from utils.bp.local_date import LocalDate
from ids.external_id_bundle import ExternalId


class TestDbHTSMaster(unittest.TestCase, AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server} server=(local) database=PORTFOLIO_MANAGEMENT_DB'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def test_basics(self):
        self.assertIsNotNone(self.hts_master)
        self.assertEquals(True, self.hts_master.get_unique_id_scheme().__eq__('DbHts'))
        self.assertIsNotNone(self.hts_master.get_db_connector())
        self.assertIsNotNone(self.hts_master.get_clock())

    def test_to_string(self):
        self.assertEquals('DbHistoricalTimeSeriesMaster[DbHts]', self.hts_master.__str__())


class DbHistoricalTimeSeriesMasterWorkerAddTest(unittest.TestCase, AbstractDbHTSMasterTest):

    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server} server=(local) database=PORTFOLIO_MANAGEMENT_DB'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def test_add_null_document(self):
        self.assertRaises(IllegalArgumentException, self.hts_master.add, *(None,))

    def test_add_all(self):
        now = Instant.now_clock(self.hts_master.get_clock())
        info = ManageableHistoricalTimeSeriesInfo()
        info.set_name('Added')
        info.set_data_field('DF')
        info.set_data_source('DS')
        info.set_data_provider('DP')
        info.set_observation_time('OT')
        id_ = ExternalIdWithDates.of(
            ExternalId.of('A', 'B'),
            LocalDate.of(2011, 6, 30),
            None)
        bundle = ExternalIdBundleWithDates.of([id_])
        info.set_external_id_bundle(bundle)
        doc = HistoricalTimeSeriesInfoDocument(info)
        test = self.hts_master.add(doc)

        unique_id = test.get_unique_id()
        self.assertIsNotNone(unique_id)
        self.assertEquals('DbHts', unique_id.get_scheme())
        self.assertTrue(unique_id.is_versioned())
        self.assertTrue(int(unique_id.get_value()) >= 1000)
        self.assertEquals('0', unique_id.get_version())
        #self.assertEquals(now, test.get_version_from_instant())
        self.assertEquals(None, test.get_version_to_instant())
        #self.assertEquals(now, test.get_correction_from_instant())
        self.assertEquals(None, test.get_correction_to_instant())
        test_info = test.get_info()
        self.assertIsNotNone(test_info)
        self.assertEquals(unique_id, test_info.get_unique_id())
        self.assertEquals('Added', test_info.get_name())
        self.assertEquals('DF', test_info.get_data_field())
        self.assertEquals('DS', test_info.get_data_source())
        self.assertEquals('DP', test_info.get_data_provider())
        self.assertEquals('OT', test_info.get_observation_time())
        self.assertEquals(1, test_info.get_external_id_bundle().size())
        self.assertTrue(id_ in test_info.get_external_id_bundle().get_external_ids())

    def test_add_and_then_get(self):
        info = ManageableHistoricalTimeSeriesInfo()
        info.set_name('Added2')
        info.set_data_field('DF2')
        info.set_data_source('DS2')
        info.set_data_provider('DP2')
        info.set_observation_time('OT2')
        id_ = ExternalIdWithDates.of(
            ExternalId.of('A2', 'B2'),
            LocalDate.of(2011, 6, 30),
            None)
        bundle = ExternalIdBundleWithDates.of([id_])
        info.set_external_id_bundle(bundle)
        doc = HistoricalTimeSeriesInfoDocument(info)
        added = self.hts_master.add(doc)
        test = self.hts_master.get(added.get_unique_id())
        self.assertEquals(added, test)


class DbHistoricalTimeSeriesMasterWorkerCorrectTest(unittest.TestCase, AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server} server=(local) database=PORTFOLIO_MANAGEMENT_DB'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def test_correct_no_hts_id(self):
        info = ManageableHistoricalTimeSeriesInfo()
        info.set_name('Corrected')
        info.set_data_field('DFC1')
        info.set_data_source('DSC1')
        info.set_data_provider('DPC1')
        info.set_observation_time('OTC1')
        id_ = ExternalIdWithDates.of(
            ExternalId.of('AC1', 'BC1'),
            LocalDate.of(2011, 6, 30),
            None)
        bundle = ExternalIdBundleWithDates.of([id_])
        info.set_external_id_bundle(bundle)
        doc = HistoricalTimeSeriesInfoDocument(info)
        self.assertRaises(IllegalArgumentException, self.hts_master.correct, *(doc,))

    def test_get(self):
        now = Instant.now_clock(self.hts_master.get_clock())
        info = ManageableHistoricalTimeSeriesInfo()
        initial_unique_id = UniqueId.of(scheme='DbHts', value='101', version = '0')
        info.set_unique_id(initial_unique_id)
        info.set_name('Corrected2')
        info.set_data_field('DFC2')
        info.set_data_source('DSC2')
        info.set_data_provider('DPC2')
        info.set_observation_time('OTC2')
        id_ = ExternalIdWithDates.of(
            ExternalId.of('AC2', 'BC2'),
            LocalDate.of(2011, 6, 30),
            None)
        bundle = ExternalIdBundleWithDates.of([id_])
        info.set_external_id_bundle(bundle)
        input_doc = HistoricalTimeSeriesInfoDocument(info)
        self.hts_master.add(input_doc)
        corrected = self.hts_master.correct(input_doc)
        old = self.hts_master.get(input_doc.get_unique_id().with_version('0'))

        self.assertEquals(False, initial_unique_id.__eq__(corrected.get_unique_id()))
        self.assertEquals(input_doc.get_version_from_instant(), corrected.get_version_from_instant())
        self.assertEquals(input_doc.get_version_to_instant(), corrected.get_version_to_instant())
        self.assertEquals(now, corrected.get_correction_from_instant())
        self.assertEquals(None, corrected.get_correction_to_instant())
        self.assertEquals(input_doc.get_info(), corrected.get_info())

        self.assertEquals(old.get_unique_id(), input_doc.get_unique_id().with_version('0'))
        self.assertEquals(input_doc.get_version_from_instant(), old.get_version_from_instant())
        self.assertEquals(input_doc.get_version_to_instant(), old.get_version_to_instant())
        self.assertEquals(input_doc.get_correction_from_instant(), old.get_correction_from_instant())
        self.assertEquals(now, old.get_correction_to_instant())

        search = HistoricalTimeSeriesInfoHistoryRequest(old.get_unique_id().with_version('0'), now, None)
        search_result = self.hts_master.history(search)
        self.assertEquals(2, len(search_result.get_documents()))


class DbHistoricalTimeSeriesMasterWorkerGetTest(unittest.TestCase, AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server} server=(local) database=PORTFOLIO_MANAGEMENT_DB'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def test_get_versioned101(self):
        info = ManageableHistoricalTimeSeriesInfo()
        info.set_name('Corrected')
        info.set_data_field('DFC1')
        info.set_data_source('DSC1')
        info.set_data_provider('DPC1')
        info.set_observation_time('OTC1')
        id_ = ExternalIdWithDates.of(
            ExternalId.of('AC1', 'BC1'),
            LocalDate.of(2011, 6, 30),
            None)
        bundle = ExternalIdBundleWithDates.of([id_])
        info.set_external_id_bundle(bundle)
        doc = HistoricalTimeSeriesInfoDocument(info)
        self.assertRaises(IllegalArgumentException, self.hts_master.correct, *(doc,))


def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestDbHTSMaster)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(DbHistoricalTimeSeriesMasterWorkerCorrectTest)
    suite3 = unittest.TestLoader().loadTestsFromTestCase(DbHistoricalTimeSeriesMasterWorkerAddTest)
    return unittest.TestSuite([suite1, suite2, suite3])

if __name__ == "__main__":
    unittest.main()






