import unittest
from db.test.hts.abstract_test_db_hts import AbstractDbHTSMasterTest

from ids.version_correction import VersionCorrection
from ids.object_id import UniqueId, ObjectId
from hts.historical_time_series_get_filter import HistoricalTimeSeriesGetFilter
from db.historical_master.db_historical_time_series_master import DbHistoricalTimeSeriesMaster
from utils.bp.local_date import LocalDate
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource


class TestDbHTSDataPointsWorkerMaster(AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server}; server=(local); database=PORTFOLIO_MANAGEMENT_DB;'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()
        self.doSetUp()


    def tearDown(self):
        self.test_map = None
        self.hts_master = None

    def test_get_UID_101_latest(self):

        unique_id = UniqueId.of(scheme="DbHts", value="DP101")
        test = self.hts_master.get_time_series(unique_id)
        self.assertEquals(unique_id.get_object_id(), test.get_unique_id().get_object_id())
        self.assertEquals(LocalDate.of(2011, 1, 1), self.hts_master.get_time_series(unique_id, filter_=HistoricalTimeSeriesGetFilter.of_earliest_point()).get_time_series().get_earliest_time())
        self.assertEquals(LocalDate.of(2011, 1, 3),
                          self.hts_master.get_time_series(unique_id,
                                                          filter_=HistoricalTimeSeriesGetFilter.of_latest_point()
                          ).get_time_series().get_latest_time())
        self.assertEquals(self._version_2_instant, test.get_version_instant())
        self.assertEquals(self._version_4_instant, test.get_correction_instant())
        time_series = test.get_time_series()
        self.assertEquals(3, time_series.size())
        self.assertEquals(LocalDate.of(2011, 1, 1), time_series.get_time_at_index(0))
        self.assertEquals(3.1, time_series.get_value_at_index(0), 0.001)
        self.assertEquals(LocalDate.of(2011, 1, 2), time_series.get_time_at_index(1))
        self.assertEquals(3.22, time_series.get_value_at_index(1), 0.001)
        self.assertEquals(LocalDate.of(2011, 1, 3), time_series.get_time_at_index(2))
        self.assertEquals(3.33, time_series.get_value_at_index(2), 0.001)

    def test_get_UID_102_latest(self):
        uniqueId = UniqueId.of(scheme="DbHts", value="DP102")
        test = self.hts_master.get_time_series(uniqueId)
        self.assertEquals(uniqueId.get_object_id(), test.get_unique_id().get_object_id())
        timeSeries = test.get_time_series()
        self.assertEquals(0, timeSeries.size())

    def test_get_UID_101_removed(self):
        uniqueId = UniqueId.of(scheme="DbHts", value="101")
        self.hts_master.remove(uniqueId)
        self.assertIsNotNone(self.hts_master.get_time_series(UniqueId.of(scheme="DbHts", value="DP101")))

    def test_get_OID_101_latest(self):
        oid = ObjectId.of(scheme="DbHts", value="DP101")
        test = self.hts_master.get_time_series(oid, VersionCorrection.LATEST())
        self.assertEquals(oid, test.get_unique_id().get_object_id())
        timeSeries = test.get_time_series()
        self.assertEquals(3, timeSeries.size())
        self.assertEquals(LocalDate.of(2011, 1, 1), timeSeries.get_time_at_index(0))
        self.assertEquals(3.1, timeSeries.get_value_at_index(0), 0.0001)
        self.assertEquals(LocalDate.of(2011, 1, 2), timeSeries.get_time_at_index(1))
        self.assertEquals(3.22, timeSeries.get_value_at_index(1), 0.0001)
        self.assertEquals(LocalDate.of(2011, 1, 3), timeSeries.get_time_at_index(2))
        self.assertEquals(3.33, timeSeries.get_value_at_index(2), 0.0001)

    def test_get_OID_101_post1(self):
        oid = ObjectId.of(scheme="DbHts", value="DP101")
        test = self.hts_master.get_time_series(oid, VersionCorrection.of_version_as_of(self._version_1_instant.plus_seconds(1)))
        self.assertEquals(oid, test.get_unique_id().get_object_id())
        timeSeries = test.get_time_series()
        self.assertEquals(3, timeSeries.size())
        self.assertEquals(LocalDate.of(2011, 1, 1), timeSeries.get_time_at_index(0))
        self.assertEquals(3.1, timeSeries.get_value_at_index(0), 0.0001)

    def test_get_OID_101_post2(self):
        oid = ObjectId.of(scheme="DbHts", value="DP101")
        test = self.hts_master.get_time_series(oid, VersionCorrection.of_version_as_of(self._version_2_instant.plus_seconds(1)))
        self.assertEquals(oid, test.get_unique_id().get_object_id())
        timeSeries = test.get_time_series()
        self.assertEquals(3, timeSeries.size())
        self.assertEquals(LocalDate.of(2011, 1, 1), timeSeries.get_time_at_index(0))
        self.assertEquals(3.1, timeSeries.get_value_at_index(0), 0.0001)
        self.assertEquals(LocalDate.of(2011, 1, 2), timeSeries.get_time_at_index(1))
        self.assertEquals(3.22, timeSeries.get_value_at_index(1), 0.0001)
        self.assertEquals(LocalDate.of(2011, 1, 3), timeSeries.get_time_at_index(2))
        self.assertEquals(3.33, timeSeries.get_value_at_index(2), 0.0001)

    def test_get_UID_101_correct_post3(self):
        oid = ObjectId.of(scheme="DbHts", value="DP101")
        base = self.hts_master.get_time_series(oid, version_correction=VersionCorrection.of(version_as_of=self._version_2_instant.plus_seconds(1),
                                                                                            corrected_to=self._version_3_instant.plus_seconds(1)))
        test = self.hts_master.get_time_series(base.get_unique_id())
        self.assertEquals(base, test)

    def test_get_dateRangeFromStart(self):
        oid = ObjectId.of("DbHts", "DP101")
        test = self.hts_master.get_time_series(oid,
            version_correction=VersionCorrection.of(version_as_of=self._version_2_instant.plus_seconds(1),
                                                    corrected_to=self._version_3_instant.plus_seconds(1)),
            filter_=HistoricalTimeSeriesGetFilter.of_range(None, LocalDate.of(2011, 1, 2)))
        self.assertEquals(oid, test.get_unique_id().get_object_id())
        timeSeries = test.get_time_series()
        self.assertEquals(2, timeSeries.size())
        self.assertEquals(LocalDate.of(2011, 1, 1), timeSeries.get_time_at_index(0))
        self.assertEquals(3.1, timeSeries.get_value_at_index(0), 0.0001)
        self.assertEquals(LocalDate.of(2011, 1, 2), timeSeries.get_time_at_index(1))
        self.assertEquals(3.21, timeSeries.get_value_at_index(1), 0.0001)


    # def test_update_102_startsEmpty(self):
    #     dates = [LocalDate.of(2011, 7, 1), LocalDate.of(2011, 7, 2), LocalDate.of(2011, 7, 4)]
    #     values = [1.1, 2.2, 3.3]
    #     series = ImmutableLocalDateDoubleTimeSeries.of(dates, values)
    #     oid = ObjectId.of("DbHts", "DP102")
    #     uniqueId = self.hts_master.update_time_series_data_points(oid, series)
    #     test = self.hts_master.get_timeseries(uniqueId)
    #     self.assertEquals(uniqueId, test.get_unique_id())
    #     self.assertEquals(series, test.get_timeseries())






def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestDbHTSDataPointsWorkerMaster)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()







