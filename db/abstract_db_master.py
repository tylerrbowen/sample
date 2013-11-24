import sys
from ids.object_id import UniqueId
from db.template.single_value_extractors import SingleValueExtractor
from utils.bp.instant import Instant
from utils.el_sql.el_sql_bundle import ElSqlBundle
from utils.el_sql.el_sql_config import ElSqlConfig


class AbstractDbMaster(object):
    """
    An abstract master for rapid implementation of a database backed master.
    This combines the various configuration elements and convenience methods
    needed for most database masters.
    """
    def __init__(self,
                 db_connector,
                 default_scheme):
        """
        db_connector: DBConnector: The database connector.
        default_scheme: String: The scheme in use for the unique identifier
        max_retries: int: The maximum number of retries.
        sql_bundle: SqlBundle: External SQL bundle.
        """
        self._db_connector = db_connector
        self._clock = db_connector.time_source()
        self._unique_id_scheme = default_scheme
        self._max_retries = 10
        self._sql_bundle = ElSqlBundle.of(ElSqlConfig.SQL_SERVER_2008(), self.__class__, sys.modules[__name__])

    def get_max_retries(self):
        return self._max_retries

    def set_max_retries(self, max_retries):
        self._max_retries = max_retries

    def get_dialect(self):
        return self.get_db_connector().get_dialect()

    def set_db_connector(self, db_connector):
        self._db_connector = db_connector

    def get_db_connector(self):
        return self._db_connector

    def get_session_factory(self):
        pass

    def get_sql_bundle(self):
        return self._sql_bundle

    def get_odbc_template(self):
        return self.get_db_connector().get_odbc_template()

    def get_transaction_template(self):
        return self.get_db_connector().get_transaction_template()

    def get_transaction_template_retrying(self, retries):
        return self.get_db_connector().get_transaction_template_retrying(retries)

    def next_id(self, sequence_name):
        template = self.get_odbc_template()
        select = self.get_dialect().sql_next_sequence_value_select(sequence_name)
        return template.query(select, rse=SingleValueExtractor())


    def set_sql_bundle(self, bundle):
        self._sql_bundle = bundle

    def get_clock(self):
        return self._clock

    def set_clock(self, clock):
        self._clock = clock

    def reset_clock(self):
        self.set_clock(self.get_db_connector().time_source())

    def now(self):
        return Instant.now_clock(self.get_clock())

    def get_unique_id_scheme(self):
        return self._unique_id_scheme

    def set_unique_id_scheme(self, unique_id_scheme):
        self._unique_id_scheme = unique_id_scheme

    def extract_oid(self, object_identifiable):
        return int(object_identifiable.get_object_id().get_value())

    def extract_row_id(self, unique_id):
        return int(unique_id.get_object_id().get_value()) + int(unique_id.get_version())

    def check_scheme(self, object_identifiable):
        if self.get_unique_id_scheme() != object_identifiable.get_scheme():
            raise Exception

    def create_object_id(self, oid):
        return UniqueId.of(self.get_unique_id_scheme(), str(oid))

    def create_unique_id(self, oid, row_id):
        return UniqueId.of(scheme=self.get_unique_id_scheme(), value=str(oid), version=str(row_id-oid))

    def __str__(self):
        return self.__class__.__name__ + '[' + \
            self.get_unique_id_scheme() + ']'




