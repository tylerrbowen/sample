import sys
from db.result_set_extractor import ResultSetExtractor
from db.abstract_document_db_master import AbstractDocumentDbMaster
from db.date_utils import DbDateUtils
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from security.security_master import SecurityMaster
from ids.external_id_bundle import ExternalId, ExternalIdBundle
from security.manageable.security_search_sorted_order import SecuritySearchSortedOrder
from security.manageable.security_search_result import SecuritySearchResult
from security.manageable.manageable_security import ManageableSecurity
from security.manageable.security_history_result import SecurityHistoryResult
from security.manageable.security_history_request import SecurityHistoryRequest
from security.manageable.security_document import SecurityDocument
from utils.paging import Paging
from ids.external_id_search import ExternalIdSearch
from utils.el_sql.el_sql_bundle import ElSqlBundle
from utils.el_sql.el_sql_config import ElSqlConfig


class DbSecurityMaster(AbstractDocumentDbMaster, SecurityMaster):
    IDENTIFIER_SCHEME_DEFAULT = "DbSec"
    ORDER_BY_MAP = {SecuritySearchSortedOrder.OBJECT_ID_ASC.title: 'oid ASC',
                    SecuritySearchSortedOrder.OBJECT_ID_DESC.title: 'oid DESC',
                    SecuritySearchSortedOrder.VERSION_FROM_INSTANT_ASC.title: 'ver_from_instant ASC',
                    SecuritySearchSortedOrder.VERSION_FROM_INSTANT_DESC.title: 'ver_from_instant DESC',
                    SecuritySearchSortedOrder.NAME_ASC.title: 'name ASC',
                    SecuritySearchSortedOrder.NAME_DESC.title: 'name DESC',
                    SecuritySearchSortedOrder.SECURITY_TYPE_ASC.title: 'sec_type ASC',
                    SecuritySearchSortedOrder.SECURITY_TYPE_DESC.title: 'sec_type DESC'}


    def __init__(self,
                 db_connector):
        super(DbSecurityMaster, self).__init__(db_connector, self.IDENTIFIER_SCHEME_DEFAULT)
        self._detail_provider = None
        self._sql_bundle = ElSqlBundle.of(ElSqlConfig.SQL_SERVER_2008(), self.__class__, sys.modules[__name__])

    def get_detail_provider(self):
        return self._detail_provider

    def set_detail_provider(self, provider):
        self._detail_provider = provider

    def meta_data(self, request):
        pass

    def search(self, request):
        """
        
        @param: request: SecuritySearchRequest
        
        returns: SecuritySearchResult
        """
        vc = request.get_version_correction().with_latest_fixed(self.now())
        result = SecuritySearchResult()
        external_id_search = request.get_external_id_search()
        object_ids = request.get_object_ids()
        if (object_ids is not None and len(object_ids) == 0) or \
                external_id_search.can_match(request.get_external_id_search()) == False:
            result.set_paging(Paging.of(request.get_paging_request(), 0))
            return result

        args = DbMapSqlParameterSource()
        args.add_timestamp('version_as_of_instant', vc.get_version_as_of())
        args.add_timestamp('corrected_to_instant', vc.get_corrected_to())
        args.add_value_null_ignored('name', self.get_dialect().sql_wildcard_adjust_value(request.get_name()))
        args.add_value_null_ignored('sec_type', request.get_security_type())
        args.add_value_null_ignored('external_id_scheme', self.get_dialect().sql_wildcard_adjust_value(request.get_external_id_scheme()))
        args.add_value_null_ignored('external_id_value', request.get_external_id_value())
        if external_id_search is not None and external_id_search.always_matches() == False:
            i = 0
            for external_id in external_id_search:
                args.add_value('key_scheme' + i.__str__(), external_id.get_scheme().get_name())
                args.add_value('key_value' + i.__str__(), external_id.get_value())
                i += 1
            args.add_value("sql_search_external_ids_type", external_id_search.get_search_type())
            args.add_value("sql_search_external_ids", self.sql_select_id_keys(external_id_search))
            args.add_value("id_search_size", external_id_search.get_external_ids().size())
        
        if object_ids is not None:
            buf = ''
            for object_id in object_ids:
                self.check_scheme(object_id)
                buf += self.extract_oid(object_id).__str__() + ', '
            
            buf = buf[:-2]
            args.add_value("sql_search_object_ids", buf)
        
        args.add_value("sort_order", self.ORDER_BY_MAP.get(request.get_sort_order()))
        args.add_value("paging_offset", request.get_paging_request().get_first_item())
        args.add_value("paging_fetch", request.get_paging_request().get_paging_size())

        detail_provider = self.get_detail_provider()  # lock against change
        if detail_provider is not None:
            detail_provider.extend_search(request, args)
        
        sql = {self.get_sql_bundle().get_sql("Search", args), self.get_sql_bundle().get_sql("SearchCount", args)}
        self.do_search(request.get_paging_request(), sql, args, SecurityDocumentExtractor(self), result)
        if request.is_full_detail():
            self.load_detail(detail_provider, result.get_documents())

        return result
        

    
    def sql_select_id_keys(self, id_search):
        """
            * Gets the SQL to find all the ids for a single bundle.
            * <p>
            * This is too complex for the elsql mechanism.
            * 
            * @param idSearch  the identifier search, not None
            * @return the SQL, not None
        """
        lst = []
        for i in range(len(id_search)):
          lst.append("(key_scheme = :key_scheme" + i.__str__() + " AND key_value = :key_value" + i.__str__() + ") ")
        return 'OR '.join(lst)
    
    def get(self, object_id=None, version_correction=None, unique_id=None):
        if unique_id is not None:
            doc = self.do_get(unique_id, SecurityDocumentExtractor(self), "Security")
        else:
            doc = self.do_get_by_oid_instants(object_id, version_correction, SecurityDocumentExtractor(self), "Security")
        self.load_detail(self.get_detail_provider(), [doc])
        return doc
    
    def history(self, request):
        result = self.do_history(request, SecurityHistoryResult(), SecurityDocumentExtractor(self))
        if request.is_full_detail():
            self.load_detail(self.get_detail_provider(), result.get_documents())
        return result
    
    def load_detail(self, detail_provider, docs):
        """
        Loads the detail of the security for the document.
        SecurityMasterDetailProvider
        List<SecurityDocument>
        void
        """
        if detail_provider is not None:
            for doc in docs:
                doc.set_security(detail_provider.load_security_detail(doc.get_security()))
        
    def insert(self, document):
        """
        Inserts a new document.
        @param document  the document, not None
        @return the new document, not None
        """
        doc_id = self.next_id('sec_security_seq')
        doc_oid = self.extract_oid(document.get_unique_id()) if document.get_unique_id() is not None else doc_id
        doc_args = DbMapSqlParameterSource()
        doc_args.add_value("doc_id", doc_id)
        doc_args.add_value("doc_oid", doc_oid)
        doc_args.add_timestamp("ver_from_instant", document.get_version_from_instant())
        doc_args.add_time_stamp_null_future("ver_to_instant", document.get_version_to_instant())
        doc_args.add_timestamp("corr_from_instant", document.get_correction_from_instant())
        doc_args.add_time_stamp_null_future("corr_to_instant", document.get_correction_to_instant())
        doc_args.add_value("name", document.get_security().get_name())
        doc_args.add_value("sec_type", document.get_security().get_security_type())
        if document.get_security().__class__ == ManageableSecurity.__class__:
            doc_args.add_value("detail_type", "R")
        else:
            doc_args.add_value("detail_type", "D")
        assoc_list = []
        id_key_list = []
        sql_select_id_key = self.get_sql_bundle().get_sql("SelectIdKey")
        for external_id in document.get_security().get_external_id_bundle():
            assoc_args = DbMapSqlParameterSource()
            assoc_args.add_value("doc_id", doc_id).\
                add_value("key_scheme", external_id.get_scheme().get_name()).\
                add_value("key_scheme", external_id.get_scheme().get_name()).\
                add_value("key_value", external_id.get_value())
            assoc_list.append(assoc_args)
            if len(self.get_odbc_template().query_for_list(sql_select_id_key, assoc_args)) == 0:
                id_key_id = self.next_id("sec_idkey_seq")
                id_key_args = DbMapSqlParameterSource()
                id_key_args.add_value("idkey_id", id_key_id).\
                    add_value("key_scheme", external_id.get_scheme().get_name()).\
                    add_value("key_value", external_id.get_value())
                id_key_list.append(id_key_args)
        sql_doc = self.get_sql_bundle().get_sql("Insert", doc_args)
        sql_id_key = self.get_sql_bundle().get_sql("InsertIdKey")
        sql_doc2id_key = self.get_sql_bundle().get_sql("InsertDoc2IdKey")
        self.get_odbc_template().update(sql_doc, doc_args)
        self.get_odbc_template().batch_update(sql_id_key, id_key_list)
        self.get_odbc_template().batch_update(sql_doc2id_key, assoc_list)
        unique_id = self.create_unique_id(doc_oid, doc_id)
        document.get_security().set_unique_id(unique_id)
        unique_id = self.create_unique_id(doc_oid, doc_id)
        document.get_security().set_unique_id(unique_id)
        document.set_unique_id(unique_id)
        detail_provider = self.get_detail_provider()
        if (detail_provider is not None):
            detail_provider.store_security_detail(document.get_security())
        attributes = dict(document.get_security().get_attributes())
        security_attribute_list = []
        for key, value in attributes.iteritems():
            securityAttrId = self.next_id("sec_security_attr_seq")
            attributeArgs = DbMapSqlParameterSource()
            attributeArgs.add_value("attr_id", securityAttrId).\
                add_value("security_id", doc_id).\
                add_value("security_oid", doc_oid).\
                add_value("key", key).\
                add_value("value", value)
            security_attribute_list.append(attributeArgs)
        sqlAttributes = self.get_sql_bundle().get_sql("InsertAttributes")
        self.get_odbc_template().batch_update(sqlAttributes, security_attribute_list)
        return document
      
    def storeRawSecurityDetail(self, security):
        pass
    
    
class SecurityDocumentExtractor(ResultSetExtractor):
    """
    Mapper from SQL rows to a SecurityDocument.
    """
    def __init__(self, caller):
        super(SecurityDocumentExtractor, self).__init__()
        self._lastdoc_id = -1
        self._security = None
        self._documents = []
        self._caller = caller
    
    def extract_data(self, rs):
        for row in rs:
            doc_id = row.doc_id #['DOC_ID']
            if self._lastdoc_id != doc_id:
                self._lastdoc_id = doc_id
                self.build_security(row, doc_id)
            id_scheme = row.key_scheme #['KEY_SCHEME']
            id_value = row.key_value #['KEY_VALUE']
            if id_scheme is not None and id_value is not None:
                external_id = ExternalId.of(id_scheme, id_value)
                self._security.set_external_id_bundle(self._security.get_external_id_bundle().with_external_id(external_id ))
            security_attr_key = row.security_attr_key #['SECURITY_ATTR_KEY']
            security_attr_value = row.security_attr_value #['SECURITY_ATTR_VALUE']
            if security_attr_key is not None and security_attr_value is not None:
                self._security.add_attribute(security_attr_key, security_attr_value)
        return self._documents
    
    def build_security(self, row, doc_id):
        doc_oid = row.doc_oid #['DOC_OID']
        version_from = row.ver_from_instant #['VER_FROM_INSTANT']
        version_to = row.ver_to_instant #['VER_TO_INSTANT']
        correction_from = row.corr_from_instant #['CORR_FROM_INSTANT']
        correction_to = row.corr_to_instant #['CORR_TO_INSTANT']
        name = row.name #['NAME']
        sec_type = row.sec_type #['SEC_TYPE']
        unique_id = self._caller.create_unique_id(doc_oid, doc_id)
        detail_type = row.detail_type #["DETAIL_TYPE"]
        self._security = ManageableSecurity(unique_id=unique_id, name=name, security_type=sec_type, external_id_bundle=ExternalIdBundle.EMPTY())
        doc = SecurityDocument(self._security)
        doc.set_version_from_instant(DbDateUtils.from_sql_timestamp(version_from))
        doc.set_version_to_instant(DbDateUtils.from_sql_timestamp_null_far_future(version_to))
        doc.set_correction_from_instant(DbDateUtils.from_sql_timestamp(correction_from))
        doc.set_correction_to_instant(DbDateUtils.from_sql_timestamp_null_far_future(correction_to))
        doc.set_unique_id(unique_id)
        self._documents.append(doc)
    
    def history_by_versions_corrections(self, request):
        history_request = SecurityHistoryRequest()
        history_request.set_corrections_to_instant(request.get_corrections_from_instant())
        history_request.set_corrections_to_instant(request.get_corrections_to_instant())
        history_request.set_versions_to_instant(request.get_versions_to_instant())
        history_request.set_versions_from_instant(request.get_versions_from_instant())
        history_request.set_object_id(request.get_object_id())
        return self._caller.history(history_request)

        