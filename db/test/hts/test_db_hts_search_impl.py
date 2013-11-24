import unittest

from db.test.hts.abstract_test_db_hts import AbstractDbHTSMasterTest
from db.historical_master.db_historical_time_series_master import DbHistoricalTimeSeriesMaster
from ids.version_correction import VersionCorrection
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from hts.historical_time_series_info_search_request import HistoricalTimeSeriesInfoSearchRequest
from ids.external_id_search import ExternalIdSearch
from analytics.financial.time_series.returns.simple_net_time_series_return_calculator import SimpleNetTimeSeriesReturnCalculator
from financial.analytics.time_series.returns.simple_gross_time_series_return_calculator import SimpleGrossTimeSeriesReturnCalculator
from utils.calculation_mode import CalculationMode
from ids.external_id import ExternalId


class DbHistoricalTimeSeriesMasterWorkerSearchImplTest(AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server}; server=(local); database=PORTFOLIO_MANAGEMENT_DB;'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()

    def test_search_oneKey_ANY_1(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "ABT"))

        test = self.hts_master.search(request)
        self.assertEquals(16, len(test.get_documents()))
        print test
        request.set_data_field('PRICE_CLOSE')
        request.set_data_provider('COMPUSTAT')
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        print test
        request.set_data_field('DIVS')
        test = self.hts_master.search(request)
        print test
        self.assertEquals(1, len(test.get_documents()))

    def test_get_series(self):
        request_price = HistoricalTimeSeriesInfoSearchRequest()
        request_price.add_external_id(ExternalId.of("TICKER", "ABT"))
        request_price.set_data_field('PRICE_CLOSE')
        request_price.set_data_provider('COMPUSTAT')
        test_price = self.hts_master.search(request_price)
        request_divs = HistoricalTimeSeriesInfoSearchRequest()
        request_divs.add_external_id(ExternalId.of("TICKER", "ABT"))
        request_divs.set_data_field('DIVS')
        request_divs.set_data_provider('COMPUSTAT')
        test_divs = self.hts_master.search(request_divs)
        info_price = test_price.get_first_info()
        info_divs = test_divs.get_first_info()
        oid_price = info_price.get_unique_id().get_object_id()
        oid_divs = info_divs.get_unique_id().get_object_id()
        test_series_price = self.hts_master.get_time_series(oid_price, VersionCorrection.LATEST())
        test_series_divs = self.hts_master.get_time_series(oid_divs, VersionCorrection.LATEST())
        timeSeries_price = test_series_price.get_time_series()
        timeSeries_divs = test_series_divs.get_time_series()
        print timeSeries_price
        print timeSeries_divs

    def test_Time_series_calculator(self):
        request_price = HistoricalTimeSeriesInfoSearchRequest()
        request_price.add_external_id(ExternalId.of("TICKER", "ADT"))
        request_price.set_data_field('PRICE_CLOSE')
        request_price.set_data_provider('COMPUSTAT')
        test_price = self.hts_master.search(request_price)
        request_divs = HistoricalTimeSeriesInfoSearchRequest()
        request_divs.add_external_id(ExternalId.of("TICKER", "ADT"))
        request_divs.set_data_field('DIVS')
        request_divs.set_data_provider('COMPUSTAT')
        test_divs = self.hts_master.search(request_divs)
        info_price = test_price.get_first_info()
        info_divs = test_divs.get_first_info()
        oid_price = info_price.get_unique_id().get_object_id()
        request_new = HistoricalTimeSeriesInfoSearchRequest()
        request_new.set_data_field('DIVS')
        request_new.set_data_provider('COMPUSTAT')
        request_new.set_external_id_search(ExternalIdSearch())
        request_new.add_external_id(ExternalId.of("TICKER", "ADT"))
        test_new = self.hts_master.search(request_new)
        info_divs = test_new._documents[2]#.get_first_info()
        oid_divs = info_divs.get_unique_id().get_object_id()
        test_series_price = self.hts_master.get_time_series(oid_price, VersionCorrection.LATEST())
        test_series_divs = self.hts_master.get_time_series(oid_divs, VersionCorrection.LATEST())
        timeSeries_price = test_series_price.get_time_series()
        timeSeries_divs = test_series_divs.get_time_series()
        calculator_net = SimpleNetTimeSeriesReturnCalculator(CalculationMode.LENIENT)
        calculator_gross = SimpleGrossTimeSeriesReturnCalculator(CalculationMode.LENIENT)
        net_returns = calculator_net.evaluate(timeSeries_price, timeSeries_divs)
        gross_returns = calculator_gross.evaluate(timeSeries_price, timeSeries_divs)
        print net_returns
        print gross_returns

    # def test_search_seriesIds(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_object_id(ObjectId.of("DbHts", "101"))
    #     request.add_object_id(ObjectId.of("DbHts", "201"))
    #     request.add_object_id(ObjectId.of("DbHts", "9999"))
    #     test = self.hts_master.search(request)
    #     self.assertEquals(2, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert203(test.get_documents()[1])
    #
    # def test_search_seriesIds_badSchemeValidOid(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_object_id(ObjectId.of("Rubbish", "101"))
    #     self.assertRaises(IllegalArgumentException, self.hts_master.search, *(request,))
    #
    # def test_search_noKeys_EXACT_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_search(ExternalIdSearch())
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_noKeys_ALL_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_search(ExternalIdSearch())
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_noKeys_ANY_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_search(ExternalIdSearch())
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ANY)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_noKeys_NONE_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_search(ExternalIdSearch())
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
    #
    #
    # def test_search_oneKey_ANY_1_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("A", "Z"))
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_twoKeys_ANY_2(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("TICKER", "V503"))
    #     test = self.hts_master.search(request)
    #     self.assertEquals(2, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert102(test.get_documents()[1])
    #
    # def test_search_twoKeys_ANY_2_oneMatches(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("TICKER", "RUBBISH"))
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_twoKeys_ANY_2_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("E", "H"), ExternalId.of("A", "D"))
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_identifier(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_value("V501")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_identifier_case(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_identifier_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_value("FooBar")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_identifier_wildcard(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_value("*3")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert102(test.get_documents()[0])
    #
    # def test_search_identifier_wildcardCase(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_external_id_value("v*3")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert102(test.get_documents()[0])
    #
    # def test_search_oneKey_ALL_1(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("TICKER", "V501"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_oneKey_ALL_1_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("A", "Z"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_twoKeys_ALL_2(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("NASDAQ", "V502"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_twoKeys_ALL_2_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("A", "D"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_oneKey_NONE(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("TICKER", "V501"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(2, len(test.get_documents()))
    #     self.assert102(test.get_documents()[0])
    #     self.assert203(test.get_documents()[1])
    #
    # def test_search_oneKey_NONE_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("TICKER", "V501"))
    #     request.add_external_id(ExternalId.of("TICKER", "V503"))
    #     request.add_external_id(ExternalId.of("TICKER", "V505"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_twoKeys_EXACT(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("NASDAQ", "V502"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #
    # def test_search_threeKeys_EXACT_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.add_external_id(ExternalId.of("TICKER", "V501"))
    #     request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_name_noMatch(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_name("FooBar")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_name(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_name("N102")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert102(test.get_documents()[0])
    #
    # def test_search_name_case(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_name("n102")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(1, len(test.get_documents()))
    #     self.assert102(test.get_documents()[0])
    #
    # def test_search_name_wildcard(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_name("N1*")
    #     test = self.hts_master.search(request)
    #     self.assertEquals(2, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert102(test.get_documents()[1])
    #
    # def test_search_name_wildcardCase(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_name("n1*")
    #     test = self.hts_master.search(request)
    #
    #     self.assertEquals(2, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert102(test.get_documents()[1])
    #
    # def test_search_versionAsOf_below(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_version_correction(VersionCorrection.of_version_as_of(self._version_1_instant.minus_seconds(5)))
    #     test = self.hts_master.search(request)
    #
    #     self.assertEquals(0, len(test.get_documents()))
    #
    # def test_search_versionAsOf_mid(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_version_correction(VersionCorrection.of_version_as_of(self._version_1_instant.plus_seconds(5)))
    #     test = self.hts_master.search(request)
    #
    #     self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert102(test.get_documents()[1])
    #     self.assert201(test.get_documents()[2])
    #
    # def test_search_versionAsOf_above(self):
    #     request = HistoricalTimeSeriesInfoSearchRequest()
    #     request.set_version_correction(VersionCorrection.of_version_as_of(self._version_2_instant.plus_seconds(5)))
    #     test = self.hts_master.search(request)
    #
    #     self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
    #     self.assert101(test.get_documents()[0])
    #     self.assert102(test.get_documents()[1])
    #     self.assert203(test.get_documents()[2])
    #
    # def test_toString(self):
    #     self.assertEquals(self.hts_master.__class__.__name__ + "[DbHts]", self.hts_master.__str__())


def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(DbHistoricalTimeSeriesMasterWorkerSearchImplTest)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()



