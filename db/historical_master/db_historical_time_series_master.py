import sys

from ids.external_id_search import ExternalIdSearch, ExternalIdSearchType
from utils.argument_checker import ArgumentChecker
from utils.bp.instant import Instant
from utils.bp.duration import Duration
from utils.paging import Paging

from db.abstract_document_db_master import AbstractDocumentDbMaster
from db.date_utils import DbDateUtils
from db.result_set_extractor import ResultSetExtractor
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource

from ids.version_correction import VersionCorrection
from ids.external_id_bundle_with_dates import ExternalIdWithDates, ExternalIdBundleWithDates
from ids.external_id_bundle import ExternalId

from hts.historical_time_series_get_filter import HistoricalTimeSeriesGetFilter
from hts.historical_time_series_info_document import HistoricalTimeSeriesInfoDocument
from hts.historical_time_series_info_history_request import HistoricalTimeSeriesInfoHistoryRequest
from hts.historical_time_series_info_history_result import HistoricalTimeSeriesInfoHistoryResult
from hts.historical_time_series_info_search_request import HistoricalTimeSeriesInfoSearchRequest
from hts.manageable_historical_time_series_info import ManageableHistoricalTimeSeriesInfo
from hts.historical_time_series_info_search_result import HistoricalTimeSeriesInfoSearchResult
from db_historical_time_series_data_points_worker import DbHistoricalTimeSeriesDataPointsWorker
from named_dimension_table import NamedDimensionDbTable
from utils.el_sql.el_sql_bundle import ElSqlBundle
from utils.el_sql.el_sql_config import ElSqlConfig


class DbHistoricalTimeSeriesMaster(AbstractDocumentDbMaster):
    """
     A time-series master implementation using a database for persistence.
     <p>
     This is a full implementation of the time-series master using an SQL database.
     Full details of the API are in {@link HistoricalTimeSeriesMaster}.
     <p>
     This implementation uses two linked unique identifiers, one for the document
     and one for the time-series. They share the same scheme, but have different values
     and versions. All the methods accept both formats although where possible they
     should be treated separately.
     <p>
     The SQL is stored externally in {@code DbHistoricalTimeSeriesMaster.elsql}.
     Alternate databases or specific SQL requirements can be handled using database
     specific overrides, such as {@code DbHistoricalTimeSeriesMaster-MySpecialDB.elsql}.
     <p>
     This class is mutable but must be treated as immutable after configuration.

    The default scheme for unique identifiers.
    IDENTIFIER_SCHEME_DEFAULT
     The prefix used for data point unique identifiers.
    DATA_POINT_PREFIX
    """

    IDENTIFIER_SCHEME_DEFAULT = 'DbHts'
    DATA_POINT_PREFIX = 'DP'

    def __init__(self, db_connector):
        """
            _nameTable: NamedDimensionDbTable: Dimension table.
            _dataFieldTable: NamedDimensionDbTable: Dimension table.
            _dataSourceTable: NamedDimensionDbTable: Dimension table.
            _dataProviderTable: NamedDimensionDbTable: Dimension table.
            _observationTimeTable: NamedDimensionDbTable: Dimension table.
            _dataPointsWorker: DbHistoricalTimeSeriesDataPointsWorker: Worker.
        """
        super(DbHistoricalTimeSeriesMaster, self).__init__(
                db_connector, self.IDENTIFIER_SCHEME_DEFAULT)
        self._sql_bundle = ElSqlBundle.of(ElSqlConfig.SQL_SERVER_2008(), self.__class__, sys.modules[__name__])
        self._name_table = NamedDimensionDbTable(
            db_connector, "name", "hts_name", "hts_dimension_seq")
        self._data_field_table = NamedDimensionDbTable(
            db_connector, "data_field", "hts_data_field", "hts_dimension_seq")
        self._data_source_table = NamedDimensionDbTable(
            db_connector, "data_source", "hts_data_source", "hts_dimension_seq")
        self.data_provider_table = NamedDimensionDbTable(
            db_connector, "data_provider", "hts_data_provider", "hts_dimension_seq")
        self._observation_time_table = NamedDimensionDbTable(
            db_connector, "observation_time", "hts_observation_time", "hts_dimension_seq")
        self._data_points_worker = DbHistoricalTimeSeriesDataPointsWorker(self)
    
    def get_name_table(self):
        """
            Gets the dimension table helper.
            *
            @return the table, not None
        """
        return self._name_table
    
    def get_data_field_table(self):
        """
            Gets the dimension table helper.
            @return the table, not None
        """
        return self._data_field_table
    
    def get_data_source_table(self):
        """
        Gets the dimension table helper.
        @return the table, not None
        """
        return self._data_source_table
    
    def get_data_provider_table(self):
        """
        Gets the dimension table helper.
        @return the table, not None
        """
        return self.data_provider_table
    
    def get_observation_time_table(self):
        """
        Gets the dimension table helper.
        @return the table, not None
        """
        return self._observation_time_table
    
    def get_data_points_worker(self):
        """
        Gets the data points worker.
        @return the worker, not None
        """
        return self._data_points_worker
    
    def meta_data(self, request):
        # result = HistoricalTimeSeriesInfoMetaDataResult()
        # if request.isDataField():
        #     result.set_data_fields(self.get_data_field_table().names())
        # if request.isDataSources():
        #     result.set_data_sources(self.get_data_source_table().names())
        # if request.isDataProviders():
        #     result.set_data_providers(self.get_data_provider_table().names())
        # if request.isObservationTimes():
        #     result.set_observation_times(self.get_observation_time_table().names())
        # return result
        pass
    
    def search(self, request):
        vc = request.get_version_correction().with_latest_fixed(self.now())
        result = HistoricalTimeSeriesInfoSearchResult(version_correction=vc)
        object_ids = request.get_object_ids()
        external_id_search = request.get_external_id_search()
        if (object_ids is not None and len(object_ids) == 0) or \
                not ExternalIdSearch.can_match(external_id_search):
            result.set_paging(Paging.of(request.get_paging_request(), 0))
            return result
    
        args = DbMapSqlParameterSource()
        args.add_timestamp("version_as_of_instant", vc.get_version_as_of())
        args.add_timestamp("corrected_to_instant", vc.get_corrected_to())
        args.add_value_null_ignored(
            "name",
            self.get_dialect().sql_wildcard_adjust_value(request.get_name()))
        args.add_value_null_ignored(
            "data_field",
            self.get_dialect().sql_wildcard_adjust_value(request.get_data_field()))
        args.add_value_null_ignored(
            "data_source", self.get_dialect().sql_wildcard_adjust_value(request.get_data_source()))
        args.add_value_null_ignored(
            "data_provider",
            self.get_dialect().sql_wildcard_adjust_value(request.get_data_provider()))
        args.add_value_null_ignored(
            "observation_time",
            self.get_dialect().sql_wildcard_adjust_value(request.get_observation_time()))
        args.add_date_null_ignored(
            "id_validity_date",
            request.get_validity_date())
        args.add_value_null_ignored(
            "external_id_value",
            self.get_dialect().sql_wildcard_adjust_value(request.get_external_id_value()))
        if external_id_search is not None:
            i = 0
            for id_ in external_id_search:
                args.add_value("key_scheme" + i.__str__(), id_.get_scheme().get_name())
                args.add_value("key_value" + i.__str__(), id_.get_value())
                i += 1
        if external_id_search is not None and not external_id_search.always_matches():
            i = 0
            for id_ in external_id_search:
                args.add_value("key_scheme" + i.__str__(), id_.get_scheme().get_name())
                args.add_value("key_value" + i.__str__(), id_.get_value())
                i += 1
            args.add_value("sql_search_external_ids_type", external_id_search.get_search_type())
            args.add_value("sql_search_external_ids", self.sql_select_id_keys(external_id_search))
            args.add_value("id_search_size", len(external_id_search.get_external_ids()))
        if object_ids is not None:
            buf = ''
            for object_id in object_ids:
                self.check_scheme(object_id)
                buf += self.extract_oid(object_id).__str__() + ', '
            buf = buf[:-2]
            args.add_value("sql_search_object_ids", buf)
        args.add_value("paging_offset", request.get_paging_request().get_first_item())
        args.add_value("paging_fetch", request.get_paging_request().get_paging_size())
        sql = [self.get_sql_bundle().get_sql("Search", args), self.get_sql_bundle().get_sql("SearchCount", args)]
        self.do_search(request.get_paging_request(), sql, args, HistoricalTimeSeriesDocumentExtractor(self), result)
        return result
    
    def sql_select_id_keys(self, id_search):
        """
        /**
        Gets the SQL to find all the ids for a single bundle.
        <p>
        This is too complex for the elsql mechanism.
        *
        @param id_search  the identifier search, not None
        @return the SQL, not None
        */
        """
        lst = []
        for i in range(id_search.size()):
            lst.append("(key_scheme = :key_scheme" + i.__str__() + " AND key_value = :key_value" + i.__str__() + ") ")
        return 'or '.join(lst)
    
    def get(self, unique_id=None, object_identifiable=None, version_correction=None):
        if unique_id is not None:
            if version_correction is None:
                if unique_id.get_version() is not None and 'P' in unique_id.get_version():
                    vc = self.extract_time_series_instants(unique_id)
                    return self.get(unique_id.get_object_id(), vc)
                return self.do_get(unique_id, HistoricalTimeSeriesDocumentExtractor(self), "HistoricalTimeSeries")
            else:
                return self.do_get_by_oid_instants(
                    unique_id.get_object_id(),
                    version_correction,
                    HistoricalTimeSeriesDocumentExtractor(self),
                    "HistoricalTimeSeries")
        else:
            return self.do_get_by_oid_instants(object_identifiable,
                                               version_correction,
                                               HistoricalTimeSeriesDocumentExtractor(self),
                                               'HistoricalTimeSeries')
    
    def history(self, request):
        return self.do_history(
            request,
            HistoricalTimeSeriesInfoHistoryResult(),
            HistoricalTimeSeriesDocumentExtractor(self))
    
    def add(self, document):
        ArgumentChecker.not_null(document, 'document')
        request = HistoricalTimeSeriesInfoSearchRequest()
        request.set_data_field(document.get_info().get_data_field())
        request.set_data_source(document.get_info().get_data_source())
        request.set_data_provider(document.get_info().get_data_provider())
        request.set_observation_time(document.get_info().get_observation_time())
        request.set_external_id_search(
            ExternalIdSearch(external_ids=document.get_info().get_external_id_bundle().to_bundle(None),
                             search_type=ExternalIdSearchType.EXACT))
        result = self.search(request)
        if len(result.get_documents()) > 0:
            raise Exception
        return super(DbHistoricalTimeSeriesMaster, self).add(document)
    
    def insert(self, document):
        """
        Inserts a new document.
        *
        @param document  the document, not None
        @return the new document, not None
        """
        doc_id = self.next_id("hts_master_seq")
    
        doc_oid = self.extract_oid(document.get_unique_id()) if document.get_unique_id() is not None else doc_id
        info = document.get_info()
        doc_args = DbMapSqlParameterSource()
        doc_args.add_value("doc_id", doc_id)
        doc_args.add_value("doc_oid", doc_oid)
        doc_args.add_timestamp("ver_from_instant", document.get_version_from_instant())
        doc_args.add_time_stamp_null_future("ver_to_instant", document.get_version_to_instant())
        doc_args.add_timestamp("corr_from_instant", document.get_correction_from_instant())
        doc_args.add_time_stamp_null_future("corr_to_instant", document.get_correction_to_instant())
        doc_args.add_value("name_id", self.get_name_table().ensure(info.get_name()))
        doc_args.add_value("data_field_id", self.get_data_field_table().ensure(info.get_data_field()))
        doc_args.add_value("data_source_id", self.get_data_source_table().ensure(info.get_data_source()))
        doc_args.add_value("data_provider_id", self.get_data_provider_table().ensure(info.get_data_provider()))
        doc_args.add_value("observation_time_id", self.get_observation_time_table().ensure(info.get_observation_time()))
        
        assoc_list = []
        id_key_list = []
        sql_select_id_key = self.get_sql_bundle().get_sql("SelectIdKey")
        for id_ in info.get_external_id_bundle():
            assoc_args = DbMapSqlParameterSource()
            assoc_args .add_value("doc_id", doc_id)
            assoc_args .add_value("key_scheme", id_.get_external_id().get_scheme().get_name())
            assoc_args .add_value("key_value", id_.get_external_id().get_value())
            assoc_args .add_value("valid_from", DbDateUtils.to_sql_date_null_far_past(id_.get_valid_from()))
            assoc_args .add_value("valid_to", DbDateUtils.to_sql_date_null_far_future(id_.get_valid_to()))
            assoc_list.append(assoc_args)
            if len(self.get_odbc_template().query_for_list(sql_select_id_key, assoc_args)) == 0:
                id_key_id = self.next_id('hts_idkey_seq')
                id_key_args = DbMapSqlParameterSource()
                id_key_args.add_value('idkey_id', id_key_id)
                id_key_args.add_value('key_scheme', id_.get_external_id().get_scheme().get_name())
                id_key_args.add_value('key_value', id_.get_external_id().get_value())
                id_key_list.append(id_key_args)
        
        sqlDoc = self.get_sql_bundle().get_sql("Insert", doc_args)
        sqlIdKey = self.get_sql_bundle().get_sql("InsertIdKey")
        sqlDoc2IdKey = self.get_sql_bundle().get_sql("InsertDoc2IdKey")
        self.get_odbc_template().update(sqlDoc, doc_args)
        self.get_odbc_template().batch_update(sqlIdKey, id_key_list)
        self.get_odbc_template().batch_update(sqlDoc2IdKey, assoc_list)
        
        unique_id = self.create_unique_id(doc_oid, doc_id)
        info.set_unique_id(unique_id)
        document.set_unique_id(unique_id)
        document.get_info().set_time_series_object_id(
            unique_id.get_object_id().with_value(
                self.DATA_POINT_PREFIX + unique_id.get_value()
            )
        )
        return document
    
    def get_time_series0(self, unique_id):
        self.check_scheme(unique_id)
        if unique_id.is_versioned() and unique_id.get_value().startswith(self.DATA_POINT_PREFIX):
            vc = self.extract_time_series_instants(unique_id)
        else:
            vc = VersionCorrection.LATEST()
        return self.get_time_series(unique_id.get_object_id(), version_correction=vc)
    
    def get_time_series1(self, object_id, version_correction):
        filter_ = HistoricalTimeSeriesGetFilter.of_range(None, None)
        return self.get_time_series(object_id, version_correction=version_correction, filter_=filter_)
    
    def get_time_series2(self, unique_id, filter_):
        self.check_scheme(unique_id)
        if unique_id.is_versioned() and unique_id.get_value().startswith(self.DATA_POINT_PREFIX):
            vc = self.extract_time_series_instants(unique_id)
        else:
            vc = VersionCorrection.LATEST()
        return self.get_time_series(unique_id.get_object_id(), vc, filter_)
    
    def get_time_series(self, object_id, version_correction=None, filter_=None):
        if filter_ is None and version_correction is not None:
            return self.get_time_series1(object_id, version_correction=version_correction)
        elif filter_ is not None and version_correction is None:
            return self.get_time_series2(object_id, filter_=filter_)
        elif filter_ is not None and version_correction is not None:
            return self.get_data_points_worker().get_time_series(object_id, version_correction=version_correction, filter_=filter_)
        else:
            return self.get_time_series0(object_id)
    
    def update_time_series_data_points(self, object_id, series):
        return self.get_data_points_worker().update_time_series_data_points(object_id, series)
    
    def correct_time_series_data_points(self, object_id, series):
        return self.get_data_points_worker().correct_time_series_data_points(object_id, series)
    
    def remove_time_series_data_points(self, object_id, fromDateInclusive, toDateInclusive):
        return self.get_data_points_worker().remove_time_series_data_points(object_id, fromDateInclusive, toDateInclusive)
    
    def extract_oid(self, object_id):
        """
        /**
        Extracts the object row id_ from the object identifier.
        *
        @param object_id  the object identifier, not None
        @return the date, None if no point date
        */
        """
        value = object_id.get_object_id().get_value()
        if value.startswith(self.DATA_POINT_PREFIX):
            value = value[len(self.DATA_POINT_PREFIX):]
        return int(value)
    
    def extract_time_series_instants(self, unique_id):
        """
        /**
        Extracts the instants from the unique identifier.
        *
        @param unique_id  the unique identifier, not None
        @return the instants, version, correction, not None
        */
        """
        pos = unique_id.get_version().find('P')
        ver_str = unique_id.get_version()[:pos]
        corr_str = unique_id.get_version()[pos:]
        ver = Instant.parse(ver_str)
        corr = ver.plus(Duration.parse(corr_str))
        return VersionCorrection.of(version_as_of=ver, corrected_to=corr)

    def history_by_versions_corrections(self,
                                       request):
        history_request = HistoricalTimeSeriesInfoHistoryRequest()
        history_request.set_corrections_from_instant(request.get_corrections_from_instant())
        history_request.set_corrections_to_instant(request.get_corrections_to_instant())
        history_request.set_versions_from_instant(request.get_versions_from_instant())
        history_request.set_versions_to_instant(request.get_corrections_to_instant())
        return self.history(history_request)


class HistoricalTimeSeriesDocumentExtractor(ResultSetExtractor):
    def __init__(self,
                 caller):
        super(HistoricalTimeSeriesDocumentExtractor, self).__init__()
        self._caller = caller
        self._last_doc_id = -1
        self._documents = []
        self._info = None

    def extract_data(self, result_set, *args, **kwargs):
        for rs in result_set:
            doc_id = rs.doc_id
            if self._last_doc_id != doc_id:
                self._last_doc_id = doc_id
            self.build_historical_time_series(rs, doc_id)
            id_scheme = rs.key_scheme
            id_value = rs.key_value
            if id_scheme is not None and id_value is not None:
                valid_from = DbDateUtils.from_sql_date_null_far_past(rs.key_valid_from)
                valid_to = DbDateUtils.from_sql_date_null_far_future(rs.key_valid_to)
                id_ = ExternalIdWithDates.of(ExternalId.of(scheme=id_scheme, value=id_value),
                                             valid_from=valid_from,
                                             valid_to=valid_to)
                self._info.set_external_id_bundle(self._info.get_external_id_bundle().with_external_id(id_))
        return self._documents

    def build_historical_time_series(self, rs, doc_id):
        doc_oid = rs.doc_oid
        try:
            version_from = DbDateUtils.from_sql_timestamp(rs.ver_from_instant)
            version_to = DbDateUtils.from_sql_timestamp_null_far_future(rs.ver_to_instant)
            correction_from = DbDateUtils.from_sql_timestamp(rs.corr_from_instant)
            correction_to = DbDateUtils.from_sql_timestamp_null_far_future(rs.corr_to_instant)
            name = rs.name
            data_field = rs.data_field
            data_source = rs.data_source
            data_provider = rs.data_provider
            observation_time = rs.observation_time
            unique_id = self._caller.create_unique_id(doc_oid, doc_id)
            self._info = ManageableHistoricalTimeSeriesInfo()
            self._info.set_unique_id(unique_id)
            self._info.set_name(name)
            self._info.set_data_field(data_field)
            self._info.set_data_source(data_source)
            self._info.set_data_provider(data_provider)
            self._info.set_observation_time(observation_time)
            self._info.set_external_id_bundle(ExternalIdBundleWithDates.EMPTY())
            self._info.set_time_series_object_id(unique_id.get_object_id().with_value(self._caller.DATA_POINT_PREFIX + unique_id.get_value()))
            doc = HistoricalTimeSeriesInfoDocument(self._info)
            doc.set_version_from_instant(version_from)
            doc.set_version_to_instant(version_to)
            doc.set_correction_from_instant(correction_from)
            doc.set_correction_to_instant(correction_to)
        except Exception, e:
            print e.message
        self._documents.append(doc)



