
import unittest
from utils.bp.instant import Instant
import datetime
import pytz


class TestInstant(unittest.TestCase):
    def setUp(self):
        self.test_dt = datetime.datetime(2013, 10, 13, 23, 37, 43, 624000, pytz.utc)

    def tearDown(self):
        self.test_dt = None

    def test_to_local_datetime(self):
        tz_name = 'US/Eastern'
        instant = Instant.of(1381707463, 624000000)
        ldt = instant.to_local_datetime(tz_name)
        print ldt

    def test_parse(self):
        test_str = '2013-10-13 19:37:43'
        instant = Instant.parse(test_str)
        print instant


def testSuite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestInstant)
    return unittest.TestSuite([suite1])

if __name__ == "__main__":
    unittest.main()



