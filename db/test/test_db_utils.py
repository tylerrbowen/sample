
import unittest
from utils.bp.instant import Instant
import datetime
import pytz
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource


class TestDbMapSqlParameterSource(unittest.TestCase):
    def setUp(self):
        self.test_map = DbMapSqlParameterSource()

    def tearDown(self):
        self.test_map = None

    def test_add_time_stamp(self):
        instant = Instant.of(1381707463, 624000000)
        self.test_map.add_timestamp('test', instant)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_time_stamp_null_future(self):
        instant = Instant.of(1381707463, 624000000)
        self.test_map.add_time_stamp_null_future('test', instant)
        self.test_map.add_time_stamp_null_future('test_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_timestamp_null_ignored(self):
        instant = Instant.of(1381707463, 624000000)
        self.test_map.add_timestamp_null_ignored('test', instant)
        self.test_map.add_timestamp_null_ignored('test_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_timestamp_allow_null(self):
        instant = Instant.of(1381707463, 624000000)
        self.test_map.add_timestamp_allow_null('test', instant)
        self.test_map.add_timestamp_allow_null('test_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_date(self):
        test_date = datetime.date(2013,10,1)
        self.test_map.add_date('test_date', test_date)
        print self.test_map.values

    def test_add_date_allow_null(self):
        test_date = datetime.date(2013,10,1)
        self.test_map.add_date_allow_null('test_date', test_date)
        self.test_map.add_date_allow_null('test_date_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_date_null_ignored(self):
        test_date = datetime.date(2013,10,1)
        self.test_map.add_date_null_ignored('test_date', test_date)
        self.test_map.add_date_null_ignored('test_date_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_time(self):
        test_time = datetime.time(10, 0, 0)
        self.test_map.add_time('test_time', test_time)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_time_allow_null(self):
        test_time = datetime.time(10, 0, 0)
        self.test_map.add_time_allow_null('test_time', test_time)
        self.test_map.add_time_allow_null('test_time_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_add_time_null_ignored(self):
        test_time = datetime.time(10, 0, 0)
        self.test_map.add_time_null_ignored('test_time', test_time)
        self.test_map.add_time_null_ignored('test_time_null', None)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names

    def test_compound_add(self):
        test_time = datetime.time(10, 0, 0)
        instant = Instant.of(1381707463, 624000000)
        test_date = datetime.date(2013,10,1)
        self.test_map.add_time_null_ignored('test_time', test_time).add_date_null_ignored('test_date', test_date).add_timestamp('test', instant)
        print self.test_map.values
        print self.test_map.sql_types
        print self.test_map.type_names


def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestDbMapSqlParameterSource)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()



