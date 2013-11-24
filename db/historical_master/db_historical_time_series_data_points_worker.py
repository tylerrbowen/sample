from db.result_set_extractor import ResultSetExtractor
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from db.abstract_db_master import AbstractDbMaster
from db.transaction_callback import HTSUpdateTransactionCallback, HTSCorrectTransactionCallback
from db.transaction_callback import HTSRemoveTransactionCallback
from utils.bp.duration import Duration
from db.date_utils import DbDateUtils
from ids.version_correction import VersionCorrection
from ids.object_id import UniqueId
from source.change_event_base import ChangeType
from db.template.types import Types
from hts.manageable_historical_time_series import ManageableHistoricalTimeSeries
from time_series_pkg.date.local_date.immutable_local_date_double_time_series import ImmutableLocalDateDoubleTimeSeries


class DbHistoricalTimeSeriesDataPointsWorker(AbstractDbMaster):
    """
    A worker that provides the implementation of the data points part of the time-series master.
    The time-series data points are effectively stored completely separately from the
    information document about the time-series.
    The SQL is stored externally in {@code DbHistoricalTimeSeriesMaster.elsql}.
    Alternate databases or specific SQL requirements can be handled using database
    specific overrides, such as {@code DbHistoricalTimeSeriesMaster-MySpecialDB.elsql}.
    This class is mutable but must be treated as immutable after configuration.

    DATA_POINT_PREFIX - The prefix used for data point unique identifiers.
    """
    DATA_POINT_PREFIX = 'DP'

    def __init__(self,
                 ht_master):
        """
        @param master  the database master, not null
        """
        super(DbHistoricalTimeSeriesDataPointsWorker, self).__init__(ht_master.get_db_connector(),
                                                                     ht_master.get_unique_id_scheme())
        self._master = ht_master

    def get_master(self):
        return self._master

    def get_sql_bundle(self):
        return self._master.get_sql_bundle()

    def get_time_series(self, object_id, version_correction, filter_):

        oid = self.extract_oid(object_id)
        vc = version_correction.with_latest_fixed(self.now())

        args = DbMapSqlParameterSource()
        args.add_value('doc_oid', oid)
        args.add_timestamp('version_as_of_instant', vc.get_version_as_of())
        args.add_timestamp('corrected_to_instant', vc.get_corrected_to())
        args.add_value('start_date', DbDateUtils.to_sql_date_null_far_past(filter_.get_earliest_date()))
        args.add_value('end_date', DbDateUtils.to_sql_date_null_far_future(filter_.get_latest_date()))
        named_odbc = self.get_db_connector().get_odbc_template()

        sql_version = self.get_sql_bundle().get_sql('SelectDataPointsVersion', args)
        result = named_odbc.query(sql_version, args, ManageableHTSExtractor(self, oid))

        if result is None:
            sql_exists = self.get_sql_bundle().get_sql('SelectExistential', args)
            result = named_odbc.query(sql_exists, args, ManageableHTSExtractor(self, oid))
            if result is not None:
                result.set_time_series(ImmutableLocalDateDoubleTimeSeries.EMPTY_SERIES())
                return result
            else:
                raise Exception('Unable to find TS')

        if filter_.get_max_points() is None:
            args.add_value('order', 'ASC')
        elif filter_.get_max_points() > 0:
            args.add_value('paging_fetch', filter_.get_max_points())
            args.add_value('order', 'ASC')
        elif filter_.get_max_points() < 0:
            args.add_value('paging_fetch', -filter_.get_max_points())
            args.add_value('order', 'DESC')
        else:
            result.set_time_series(ImmutableLocalDateDoubleTimeSeries.EMPTY_SERIES())
            return result

        if filter_.get_latest_date() is None or filter_.get_earliest_date() is None \
                or not filter_.get_latest_date().is_before(filter_.get_earliest_date()):
            sql_points = self.get_sql_bundle().get_sql('SelectDataPoints', args)
            series = named_odbc.query(sql_points, args, DataPointsExtractor(self))
            result.set_time_series(series)
        else:
            result.set_time_series(ImmutableLocalDateDoubleTimeSeries.EMPTY_SERIES())

        return result

    def update_time_series_data_points(self, object_id, series):
        unique_id = self.resolve_object_id(object_id, VersionCorrection.LATEST())
        if len(series) == 0:
            return unique_id
        result = self.get_transaction_template_retrying(self.get_max_retries()).execute(HTSUpdateTransactionCallback(self, unique_id, series))
        self.get_master().change_manager().entity_changed(ChangeType.CHANGED, object_id.get_object_id(), None, None, result[1])
        return result[0]

    def insert_data_points_check_max_date(self, unique_id, series):
        """
        Checks the data points can be inserted.
        @param uniqueId  the unique identifier, not null
        @param series  the time-series data points, not empty, not null
        """
        doc_oid = self.extract_oid(unique_id)
        vc = self.get_master().extract_time_series_instants(unique_id)
        query_args = DbMapSqlParameterSource()
        query_args.add_value('doc_oid', doc_oid)
        query_args.add_timestamp('ver_instant', vc.get_version_as_of())
        query_args.add_timestamp('corr_instant', vc.get_corrected_to())
        sql = self.get_sql_bundle().get_sql('SelectMaxPointDate', query_args)
        result = self.get_db_connector().get_odbc_template().query_for_list(sql, query_args)
        try:
            result = result[0]
        except (IndexError, AttributeError):
            return
        max_date = DbDateUtils.from_sql_date_allow_null(result)
        if not series.get_earliest_time().is_after(max_date):
            raise TypeError("Unable to update data points of time-series ")

    def insert_data_points(self, unique_id, series, now):
        """
        Inserts the data points.
        @param uniqueId  the unique identifier, not null
        @param series  the time-series data points, not empty, not null
        @param now  the current instant, not null
        @return the unique identifier, not null
        """
        doc_oid = self.extract_oid(unique_id)
        now_ts = DbDateUtils.to_sql_timestamp(now)
        args_list = []
        for entry in series.iteritems():
            date = entry[0]
            value = entry[0]
            if date is None or value is None:
                raise TypeError
            args = DbMapSqlParameterSource()
            args.add_value('doc_oid', doc_oid)
            args.add_value('point_date', date)
            args.add_value('ver_instant', now_ts)
            args.add_value('corr_instant', now_ts)
            args.add_value('point_value', value)
            args_list.append(args)
        sql_insert = self.get_sql_bundle().get_sql('InsertDataPoint')
        self.get_odbc_template().batch_update(sql_insert, args_list)
        return self.create_time_series_unique_id(doc_oid, now, now)

    def correct_time_series_data_points(self, object_id, series):
        """

        """
        unique_id = self.resolve_object_id(object_id, VersionCorrection.LATEST())
        if len(series) == 0:
            return unique_id
        result = self.get_transaction_template_retrying(self.get_max_retries()).execute(HTSCorrectTransactionCallback(self, unique_id, series))
        self.get_master().change_manager().entity_changed(ChangeType.CHANGED, object_id.get_object_id(), None, None, result[1])
        return result[0]

    def correct_data_points(self, unique_id, series, now):
        """
        Corrects the data points.
        @param uniqueId  the unique identifier, not null
        @param series  the time-series data points, not empty, not null
        @param now  the current instant, not null
        @return the unique identifier, not null

        """
        doc_oid = self.extract_oid(unique_id)
        now_ts = DbDateUtils.to_sql_timestamp(now)
        args_list = []
        for entry in series.iteritems():
            date = entry[0]
            value = entry[0]
            if date is None or value is None:
                raise TypeError
            args = DbMapSqlParameterSource()
            args.add_value('doc_oid', doc_oid)
            args.add_value('point_date', date)
            args.add_value('corr_instant', now_ts)
            args.add_value('point_value', value)
            args_list.append(args)
        sql_insert = self.get_sql_bundle().get_sql('InsertCorrectDataPoint')
        self.get_odbc_template().batch_update(sql_insert, args_list)
        return self.resolve_object_id(doc_oid, VersionCorrection.of(now, now))

    def remove_time_series_data_points(self, object_id, from_date_inclusive, to_date_inclusive):

        unique_id = self.resolve_object_id(object_id, VersionCorrection.LATEST())
        result = self.get_transaction_template_retrying(self.get_max_retries()).execute(HTSRemoveTransactionCallback(
            self, unique_id, from_date_inclusive, to_date_inclusive))
        self.get_master().change_manager().entity_changes(ChangeType.CHANGED, object_id.get_object_id(), None, None, result[1])
        return result[0]

    def remove_data_points(self, unique_id, from_date_inclusive, to_date_inclusive, now):
        """
        Removes data points.
        @param uniqueId  the unique identifier, not null
        @param fromDateInclusive  the start date to remove from, not null
        @param toDateInclusive  the end date to remove to, not null
        @param now  the current instant, not null
        @return the unique identifier, not null
        """
        doc_oid = self.extract_oid(unique_id)
        query_args = DbMapSqlParameterSource()
        query_args.add_value('doc_oid', doc_oid)
        query_args.add_value('start_date', DbDateUtils.to_sql_date_null_far_past(from_date_inclusive))
        query_args.add_value('end_date', DbDateUtils.to_sql_date(to_date_inclusive))
        sql_remove = self.get_sql_bundle().get_sql('SelectRemoveDataPoints')
        dates = self.get_odbc_template().query_for_list(sql_remove, query_args)
        now_ts = DbDateUtils.to_sql_timestamp(now)
        args_list = []
        for date in dates:
            args = DbMapSqlParameterSource()
            args.add_value('doc_oid', doc_oid)
            args.add_value('point_date', date.get('POINT_DATE'))
            args.add_value('corr_instant', now_ts)
            args.add_value('point_value', None, Types.DOUBLE)
            args_list.append(args)

        sql_insert = self.get_sql_bundle().get_sql('InsertCorrectDataPoint')
        self.get_odbc_template().batch_update(sql_insert, args_list)
        return self.resolve_object_id(doc_oid, VersionCorrection.of(now, now))

    def extract_oid(self, object_identifiable):
        """
        Extracts the object row id from the object identifier.
        @param objectId  the object identifier, not null
        @return the date, null if no point date
        """
        return self.get_master().extract_oid(object_identifiable)

    def create_time_series_unique_id(self, oid, ver_instant, corr_instant):
        """
        Creates a unique identifier.
        @param oid  the object identifier
        @param verInstant  the version instant, not null
        @param corrInstant  the correction instant, not null
        @return the unique identifier
        """
        oid_str = self.DATA_POINT_PREFIX + oid.__str__()
        dur = Duration.between(ver_instant, corr_instant)
        ver_str = ver_instant.__str__() + dur.__str__()
        return UniqueId.of(scheme=self.get_unique_id_scheme(),
                           value=oid_str,
                           version=ver_str)

    def extract_row_id(self, unique_id):

        pos = unique_id.get_version().index('P')
        if pos < 0:
            return super(DbHistoricalTimeSeriesDataPointsWorker, self).extract_row_id(unique_id)
        vc = self.get_master().extract_time_series_instants(unique_id)
        doc = self.get_master().get(unique_id.get_object_id(), vc)
        return super(DbHistoricalTimeSeriesDataPointsWorker, self).extract_row_id(doc.get_unique_id())

    def resolve_object_id(self, object_id, version_correction):
        """
        Resolves an object identifier to a unique identifier.
        @param objectId  the time-series object identifier, not null
        @param versionCorrection  the version-correction locator to search at, not null
        @return the time-series, not null
        """
        self.check_scheme(object_id)
        oid = self.extract_oid(object_id)
        version_correction = version_correction.with_latest_fixed(self.now())
        args = DbMapSqlParameterSource()
        args.add_value('doc_oid', oid)
        args.add_timestamp('version_as_of_instant', version_correction.get_version_as_of())
        args.add_timestamp('correct_to_instant', version_correction.get_corrected_to())
        named_odbc = self.get_db_connector().get_odbc_template()
        extractor = UniqueIdExtractor(self, oid)
        sql = self.get_sql_bundle().get_sql('SelectUniqueIdByVersionCorrection', args)
        unique_id = named_odbc.query(sql, args, extractor)
        if unique_id is None:
            raise Exception
        return unique_id


class DataPointsExtractor(ResultSetExtractor):
    """
    Mapper from SQL rows to a LocalDateDoubleTimeSeries.
    """
    def __init__(self,
                 caller):
        super(DataPointsExtractor, self).__init__()
        self._caller = caller

    def extract_data(self, result_set, *args, **kwargs):
        dates = []
        values = []
        last = None
        for rs in result_set:
            date = DbDateUtils.from_sql_date_allow_null(rs.point_date)
            if not date.__eq__(last):
                last = date
                value = rs.point_value
                if value is not None:
                    dates.append(date)
                    values.append(value)
                else:
                    raise RuntimeError
        return ImmutableLocalDateDoubleTimeSeries.of(dates, values)


class UniqueIdExtractor(ResultSetExtractor):
    """
    Mapper from SQL rows to a UniqueId.
    """
    def __init__(self,
                 caller,
                 object_id):
        super(UniqueIdExtractor, self).__init__()
        self._caller = caller
        self._object_id = object_id

    def extract_data(self, result_set, *args, **kwargs):
        for rs in result_set:
            ver = rs.max_ver_instant
            corr = rs.max_corr_instant
            if ver is None:
                ver = rs.ver_from_instant
                corr = rs.corr_from_instant
            ver_instant = DbDateUtils.from_sql_timestamp(ver)
            corr_instant = DbDateUtils.from_sql_timestamp(corr) if corr is not None else ver_instant
            return self._caller.create_time_series_unique_id(self._object_id, ver_instant, corr_instant)
        return None


class ManageableHTSExtractor(ResultSetExtractor):
    """
    Mapper from SQL rows to a ManageableHistoricalTimeSeries.
    """
    def __init__(self,
                 caller,
                 object_id):
        super(ManageableHTSExtractor, self).__init__()
        self._caller = caller
        self._object_id = object_id

    def extract_data(self, result_set, *args, **kwargs):
        for rs in result_set:
            ver = rs.max_ver_instant
            corr = rs.max_corr_instant
            ver_instant = DbDateUtils.from_sql_timestamp(ver) if ver is not None else None
            corr_instant = DbDateUtils.from_sql_timestamp(corr) if corr is not None else None
            hts = ManageableHistoricalTimeSeries()
            hts.set_unique_id(self._caller.create_time_series_unique_id(self._object_id, ver_instant, corr_instant))
            hts.set_version_instant(ver_instant)
            hts.set_correction_instant(corr_instant)
            return hts
        return None