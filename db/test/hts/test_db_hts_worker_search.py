from db.test.hts.abstract_test_db_hts import AbstractDbHTSMasterTest
from ids.version_correction import VersionCorrection
from ids.object_id import UniqueId, ObjectId
from db.historical_master.db_historical_time_series_master import DbHistoricalTimeSeriesMaster
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from hts.historical_time_series_info_search_request import HistoricalTimeSeriesInfoSearchRequest
from utils.paging import PagingRequest
from utils.argument_checker import IllegalArgumentException
from ids.external_id_search import ExternalIdSearch, ExternalIdSearchType
from ids.external_id import ExternalId
import unittest


class DbHistoricalTimeSeriesMasterWorkerSearchTest(AbstractDbHTSMasterTest):
    def setUp(self):
        self.name = 'TestHTSMaster'
        self.connection_string = 'driver={sql server}; server=(local); database=PORTFOLIO_MANAGEMENT_DB;'
        self.db_connector = None
        self.init_db_connector()
        self.hts_master = DbHistoricalTimeSeriesMaster(self.db_connector)
        self.test_map = DbMapSqlParameterSource()
        self.doSetUp()

    def test_search_documents(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        test = self.hts_master.search(request)
        #self.assertEquals(PagingRequest.FIRST_PAGE(), test.get_paging().get_request())
        self.assertEquals(self._totalHistoricalTimeSeries + 97, test.get_paging().get_total_items())
        self.assertEquals(self._totalHistoricalTimeSeries + 97, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
    
    def test_search_pageOne(self):
        pr = PagingRequest.ofPage(1, 2)
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_paging_request(pr)
        test = self.hts_master.search(request)
        self.assertEquals(pr, test.get_paging().get_request())
        #self.assertEquals(self._totalHistoricalTimeSeries, test.get_paging().get_total_items())
        #self.assertEquals(2, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])

    def test_search_pageTwo(self):
        pr = PagingRequest.ofPage(2, 2)
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_paging_request(pr)
        test = self.hts_master.search(request)
        self.assertEquals(pr, test.get_paging().get_request())
        self.assertEquals(self._totalHistoricalTimeSeries, test.get_paging().get_total_items())
        self.assertEquals(1, len(test.get_documents()))
        self.assert203(test.get_documents()[0])
    
    def test_search_seriesIds_NONE(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_object_ids([])
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
       
    def test_search_seriesIds(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_object_id(ObjectId.of("DbHts", "101"))
        request.add_object_id(ObjectId.of("DbHts", "201"))
        request.add_object_id(ObjectId.of("DbHts", "9999"))
        test = self.hts_master.search(request)
        self.assertEquals(2, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert203(test.get_documents()[1])

    def test_search_seriesIds_badSchemeValidOid(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_object_id(ObjectId.of("Rubbish", "101"))
        self.assertRaises(IllegalArgumentException, self.hts_master.search, *(request,))      
    
    def test_search_noKeys_EXACT_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_search(ExternalIdSearch())
        request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
        
    def test_search_noKeys_ALL_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_search(ExternalIdSearch())
        request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
        
    def test_search_noKeys_ANY_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_search(ExternalIdSearch())

        request.get_external_id_search().set_search_type(ExternalIdSearchType.ANY)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
       
    def test_search_noKeys_NONE_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_search(ExternalIdSearch())
        request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
        test = self.hts_master.search(request)
        self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
    
    def test_search_oneKey_ANY_1(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "V501"))
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
    
    def test_search_oneKey_ANY_1_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("A", "Z"))
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
    
    def test_search_twoKeys_ANY_2(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("TICKER", "V503"))
        test = self.hts_master.search(request)
        self.assertEquals(2, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])
    
    def test_search_twoKeys_ANY_2_oneMatches(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("TICKER", "RUBBISH"))
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
    
    def test_search_twoKeys_ANY_2_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("E", "H"), ExternalId.of("A", "D"))
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
 
    def test_search_identifier(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_value("V501")
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        
    def test_search_identifier_case(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
       
    def test_search_identifier_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_value("FooBar")
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
        
    def test_search_identifier_wildcard(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_value("*3")
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert102(test.get_documents()[0])
       
    def test_search_identifier_wildcardCase(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_external_id_value("v*3")
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert102(test.get_documents()[0])  
    
    def test_search_oneKey_ALL_1(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "V501"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
       
    def test_search_oneKey_ALL_1_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("A", "Z"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
    
    def test_search_twoKeys_ALL_2(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("NASDAQ", "V502"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])

    def test_search_twoKeys_ALL_2_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("A", "D"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.ALL)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))
    
    def test_search_oneKey_NONE(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "V501"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
        test = self.hts_master.search(request)
        self.assertEquals(2, len(test.get_documents()))
        self.assert102(test.get_documents()[0])
        self.assert203(test.get_documents()[1])

    def test_search_oneKey_NONE_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "V501"))
        request.add_external_id(ExternalId.of("TICKER", "V503"))
        request.add_external_id(ExternalId.of("TICKER", "V505"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.NONE)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))

    def test_search_twoKeys_EXACT(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_ids(ExternalId.of("TICKER", "V501"), ExternalId.of("NASDAQ", "V502"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert101(test.get_documents()[0])

    def test_search_threeKeys_EXACT_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.add_external_id(ExternalId.of("TICKER", "V501"))
        request.get_external_id_search().set_search_type(ExternalIdSearchType.EXACT)
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))

    def test_search_name_noMatch(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_name("FooBar")
        test = self.hts_master.search(request)
        self.assertEquals(0, len(test.get_documents()))

    def test_search_name(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_name("N102")
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert102(test.get_documents()[0])

    def test_search_name_case(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_name("n102")
        test = self.hts_master.search(request)
        self.assertEquals(1, len(test.get_documents()))
        self.assert102(test.get_documents()[0])

    def test_search_name_wildcard(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_name("N1*")
        test = self.hts_master.search(request)
        self.assertEquals(2, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])

    def test_search_name_wildcardCase(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_name("n1*")
        test = self.hts_master.search(request)

        self.assertEquals(2, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])

    def test_search_versionAsOf_below(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_version_correction(VersionCorrection.of_version_as_of(self._version_1_instant.minus_seconds(5)))
        test = self.hts_master.search(request)

        self.assertEquals(0, len(test.get_documents()))

    def test_search_versionAsOf_mid(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_version_correction(VersionCorrection.of_version_as_of(self._version_1_instant.plus_seconds(5)))
        test = self.hts_master.search(request)

        self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])
        self.assert201(test.get_documents()[2])

    def test_search_versionAsOf_above(self):
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_version_correction(VersionCorrection.of_version_as_of(self._version_2_instant.plus_seconds(5)))
        test = self.hts_master.search(request)

        self.assertEquals(self._totalHistoricalTimeSeries, len(test.get_documents()))
        self.assert101(test.get_documents()[0])
        self.assert102(test.get_documents()[1])
        self.assert203(test.get_documents()[2])  
    
    def test_toString(self):
        self.assertEquals(self.hts_master.__class__.__name__ + "[DbHts]", self.hts_master.__str__())
    

def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(DbHistoricalTimeSeriesMasterWorkerSearchTest)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()


