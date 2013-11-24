import logging
import datetime as dt
from connector import Connector
from utils.bp.clock import Clock
from db.date_utils import DbDateUtils
import calendar
import time


class DbConnector(Connector):
    s_logger = logging.Logger('DbConnector')

    def __init__(self,
                 name,
                 dialect,
                 data_source,
                 template,
                 transaction_template):
        """
        :param data_source: DataSource
        :param name: String
        :param dialect: DBDialect
        :param template: ODBCNameParamsTemplate
        :param transaction_template: TransactionTemplate
        """
        super(DbConnector, self).__init__()
        self._name = name
        self._data_source = data_source
        self._odbc_template = template
        self._transaction_template = transaction_template
        self._dialect = dialect
        self._clock = DbClock(self)

    def close(self):
        self.get_data_source().close()

    def get_name(self):
        return self._name

    def get_type(self):
        return self.__class__

    def get_odbc_template(self):
        return self._odbc_template

    def get_data_source(self):
        return self._data_source

    def get_dialect(self):
        return self._dialect

    def get_operations(self):
        return self._odbc_template.get_odbc_operations()

    def now(self):
        return dt.datetime.now()

    def now_db(self):
        return self.get_odbc_template().query_for_list(self.get_dialect().sql_select_now(), None)[0]

    def get_transaction_template(self):
        return self._transaction_template

    def execute(self, qry):
        connection = self._data_source.get_connection()
        cursor = connection.cursor()
        result = cursor.execute(qry)
        return result

    def get_transaction_template_retrying(self, retries):
        return TransactionTemplateRetrying(retries,self.get_transaction_template())

    def get_transaction_manager(self):
        return self.get_transaction_template().get_transaction_manager()

    def time_source(self):
        return self._clock

    def __str__(self):
        return self.__class__.__name__ + '[' + self._name + ']'


class TransactionTemplateRetrying(object):
    def __init__(self, retries, transaction_template):
        self._retries = retries
        self._transaction_template = transaction_template

    def execute(self, action):
        for retry in range(self._retries):
            try:
                return self._transaction_template.execute(action)
            except Exception, e:
                raise Exception('Execution failure', e)




class DbClock(Clock):

    def __init__(self,
                 db_connector):
        self._connector = db_connector
        self._precision = db_connector.get_dialect().get_timestamp_precision()
        self._zone = 'UTC'
        now = calendar.timegm(time.gmtime())*1000000000
        self._now_nano_time = now
        self._now_instant = None

    def instant(self):
        now_nanos = calendar.timegm(time.gmtime())*1000000000
        if now_nanos - (self._now_nano_time + 1000000000) > 0 or self._now_instant is None:
            self._now_instant = DbDateUtils.from_sql_timestamp(self._connector.now_db()).truncated_to(self._precision)
            self._now_nano_time = calendar.timegm(time.gmtime())*1000000000
            return self._now_instant
        now_nanos = calendar.timegm(time.gmtime())*1000000000
        interpolate = max(now_nanos - self._now_nano_time, 0)
        precision_nano = self._precision.get_duration().get_nano()
        interpolate = (interpolate / precision_nano) * precision_nano
        result = self._now_instant.plus_nanos(interpolate)
        return result

    def get_zone(self):
        return 'UTC'

    def with_zone(self, zone):
        return self

    def __str__(self):
        return 'DbClock'

    def __eq__(self, other):
        return False

    def __hash__(self):
        return 'UTC'.__hash__() + 1










