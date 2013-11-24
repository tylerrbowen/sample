import datetime as dt
from db.abstract_db_master import AbstractDbMaster
from db.template.db_map_sql_parameter_source import DbMapSqlParameterSource
from source.change_manager_base import BasicChangeManager
from ids.version_correction import VersionCorrection
from utils.paging import PagingRequest, Paging
from utils.argument_checker import ArgumentChecker
from db.date_utils import DbDateUtils
from source.change_event_base import ChangeType
from abstracts.abstract_history_request import AbstractHistoryRequestPreviousDocument
from abstracts.abstract_history_request import AbstractHistoryRequestAllCurrent
from abstracts.abstract_history_request import AbstractHistoryRequestCurrentInRange
from utils.master_utils import MasterUtils
from utils.exceptions.data_not_found_exception import DataNotFoundException
from transaction_callback import AddTransactionCallback
from transaction_callback import UpdateTransactionCallback
from transaction_callback import RemoveTransactionCallback
from transaction_callback import CorrectTransactionCallback
from transaction_callback import ReplaceTransactionCallback
from transaction_callback import ReplaceAllTransactionCallback
from transaction_callback import ReplaceVersionsTransactionCallback


class AbstractDocumentDbMaster(AbstractDbMaster):
    """
    An abstract master for rapid implementation of a standard version-correction
    document database backed master.
    This provides common implementations of methods in a standard {@link AbstractMaster}.
    This class is mutable but must be treated as immutable after configuration.
    """
    def __init__(self,
                 db_connector,
                 default_scheme):
        super(AbstractDocumentDbMaster, self).__init__(db_connector,
                                                       default_scheme)
        self._change_manager = BasicChangeManager()

    def get_change_manager(self):
        return self._change_manager

    def set_change_manager(self, change_manager):
        self._change_manager = change_manager

    def change_manager(self):
        return self.get_change_manager()

    def do_get(self,
               unique_id=None,
               extractor=None,
               master_name=''):
        """
        Performs a standard get by unique identifier, handling exact version or latest.
        """
        self.check_scheme(unique_id)
        if unique_id.is_versioned():
            return self.do_get_by_id(unique_id,
                                     extractor,
                                     master_name)
        else:
            return self.do_get_by_oid_instants(unique_id,
                                               VersionCorrection.LATEST(),
                                               extractor,
                                               master_name)

    def do_get_by_oid_instants(self,
                               object_id,
                               version_correction,
                               extractor,
                               master_name):
        """
        Performs a standard get by object identifier at instants.
            @param objectId  the object identifier, not null
            @param versionCorrection  the version-correction locator, not null
            @param extractor  the extractor to use, not null
            @param masterName  a name describing the contents of the master for an error message, not null
            @return the document, null if not found
        """
        try:
            if version_correction is not None:
                if version_correction.contains_latest():
                    vc = version_correction.with_latest_fixed(self.now())
                else:
                    vc = version_correction
            else:
                vc = VersionCorrection.LATEST()
            args = self.args_get_by_oid_instants(object_id, vc)
            named_odbc_operations = self.get_db_connector().get_odbc_template()
            sql = self.get_sql_bundle().get_sql('GetByOidInstants', args)
            docs = named_odbc_operations.query(sql, args, extractor)
            try:
                if len(docs) == 0:
                    raise DataNotFoundException(master_name + ' not found: ' + object_id.__str__())
                return docs[0]
            except TypeError:
                return None
        finally:
            pass


    def args_get_by_oid_instants(self,
                                 object_id,
                                 version_correction):
        """
        Gets the SQL arguments to use for a standard get by object identifier at instants.
        @param object_id  the object identifier, not null
        @param version_correction  the version-correction locator with instants fixed, not null
        @return the SQL arguments, not null
        """
        doc_oid = self.extract_oid(object_id)
        args = DbMapSqlParameterSource()
        args.add_value('doc_oid', doc_oid)
        args.add_timestamp('version_as_of', version_correction.get_version_as_of())
        args.add_timestamp('corrected_to', version_correction.get_corrected_to())
        return args

    def do_get_by_id(self,
                     unique_id,
                     extractor,
                     master_name):
        """
        Performs a standard get by versioned unique identifier.
        @param uniqueId  the versioned unique identifier, not null
        @param extractor  the extractor to use, not null
        @param masterName  a name describing the contents of the master for an error message, not null
        @return the document, null if not found
        """
        args = self.args_get_by_id(unique_id)
        named_odbc_ops = self.get_db_connector().get_odbc_template()
        sql = self.get_sql_bundle().get_sql('GetById', args)
        docs = named_odbc_ops.query(sql, args, extractor)
        if len(docs) == 0:
            raise DataNotFoundException(master_name + ' not found: ' + unique_id.__str__())
        return docs[0]

    def args_get_by_id(self,
                       unique_id):
        """
        Gets the SQL arguments to use for a standard get by versioned unique identifier.
        @param uniqueId  the versioned unique identifier, not null
        @return the SQL arguments, not null
        """
        args = DbMapSqlParameterSource()
        args.add_value('doc_oid', self.extract_oid(unique_id))
        args.add_value('doc_id', self.extract_row_id(unique_id))
        return args

    def do_history(self,
                   request,
                   result,
                   extractor):
        """
        Performs a standard history search.
        @param <R>  the document result type
        @param request  the request, not null
        @param result  the result to populate, not null
        @param extractor  the extractor to use, not null
        @return the populated result, not null
        """
        self.check_scheme(request.get_object_id())
        args = self.args_history(request)
        sql = [self.get_sql_bundle().get_sql('History', args), self.get_sql_bundle().get_sql('HistoryCount', args)]
        self.search_with_paging(request.get_paging_request(), sql, args, extractor, result)
        return result

    def args_history(self,
                     request):
        """
        Gets the SQL arguments to use for searching the history of a document.
        @param request  the request, not null
        @return the SQL arguments, not null
        """
        args = DbMapSqlParameterSource()
        args.add_value('doc_oid', self.extract_oid(request.get_object_id()))
        args.add_timestamp_null_ignored('versions_from_instant', request.get_versions_from_instant())
        args.add_timestamp_null_ignored('versions_to_instant', request.get_versions_to_instant())
        args.add_timestamp_null_ignored('corrections_from_instant', request.get_corrections_from_instant())
        args.add_timestamp_null_ignored('corrections_to_instant', request.get_corrections_to_instant())
        if request.get_versions_from_instant() is not None and \
                request.get_versions_from_instant() == request.get_versions_to_instant():
            args.add_value('sql_history_versions', 'Point')
        else:
            args.add_value('sql_history_versions', 'Range')
        if request.get_corrections_from_instant() is not None and \
                request.get_corrections_from_instant() == request.get_corrections_to_instant():
            args.add_value('sql_history_corrections', 'Point')
        else:
            args.add_value('sql_history_corrections', 'Range')
        args.add_value('paging_offset', request.get_paging_request().get_first_item())
        args.add_value('paging_fetch', request.get_paging_request().get_paging_size())
        return args

    def do_search(self,
                  paging_request,
                  sql,
                  args,
                  extractor,
                  result):
        """
        Searches for documents with paging.
        @param <T>  the type of the document
        @param paging_request  the paging request, not null
        @param sql  the array of SQL, query and count, not null
        @param args  the query arguments, not null
        @param extractor  the extractor of results, not null
        @param result  the object to populate, not null
        """
        self.search_with_paging(paging_request,
                                sql,
                                args,
                                extractor,
                                result)

    def search_with_paging(self,
                           paging_request,
                           sql,
                           args,
                           extractor,
                           result):
        """
        Searches for documents with paging.
        @param <T>  the type of the document
        @param paging_request  the paging request, not null
        @param sql  the array of SQL, query and count, not null
        @param args  the query arguments, not null
        @param extractor  the extractor of results, not null
        @param result  the object to populate, not null
        """
        named_odbc_ops = self.get_db_connector().get_odbc_template()
        if paging_request == PagingRequest.ALL():
            result.get_documents().extend(named_odbc_ops.query(sql[0], args, extractor))
            result.set_paging(Paging.of(paging_request, collection_docs=result.get_documents()))
        else:
            count = named_odbc_ops.query_for_list(sql[1], args)[0]
            result.set_paging(Paging.of(paging_request, count))
            if count > 0 and not paging_request == PagingRequest.NONE():
                result.get_documents().extend(named_odbc_ops.query(sql[0], args, extractor))

    def add(self, doc):
        added = self.get_transaction_template_retrying(self.get_max_retries()).execute(
            AddTransactionCallback(self, doc)
        )
        self.change_manager().entity_changed(ChangeType.ADDED,
                                             added.get_object_id(),
                                             added.get_version_from_instant(),
                                             added.get_version_to_instant(),
                                             self.now())
        return added

    def do_add_in_transaction(self, document):
        """
        Processes the document add, within a retrying transaction.
        @param document  the document to add, not null
        @return the added document, not null
        """
        now = self.now()
        document.set_version_from_instant(now)
        document.set_version_to_instant(None)
        document.set_correction_from_instant(now)
        document.set_correction_to_instant(None)
        document.set_unique_id(None)
        self.insert(document)
        return document

    def update(self, document):
        self.check_scheme(document.get_unique_id())
        before_id = document.get_unique_id()
        assert(before_id.is_versioned())
        updated = self.get_transaction_template_retrying(self.get_max_retries()).execute(
            UpdateTransactionCallback(self, before_id=before_id, document=document)
        )
        self.get_change_manager().entity_changed(ChangeType.CHANGED,
                                                 updated.get_object_id(),
                                                 updated.get_version_from_instant(),
                                                 self.now())
        return updated

    def do_update_in_transaction(self,
                                 before_id,
                                 document):
        """
        Processes the document update, within a retrying transaction.
        @param before_id the original identifier of the document, not null
        @param document the document to update, not null
        @return the updated document, not null
        """
        old_doc = self.get_check_latest_version(before_id)
        now = self.now()
        old_doc.set_version_to_instant(now)
        old_doc.set_correction_to_instant(now)
        self.update_version_to_instant(old_doc)
        document.set_version_from_instant(now)
        document.set_version_to_instant(None)
        document.set_correction_from_instant(now)
        document.set_correction_to_instant(None)
        document.set_unique_id(old_doc.get_unique_id().to_latest())
        self.merge_none_updated_fields(document, old_doc)
        self.insert(document)

    def remove(self, object_identifiable):
        """

        """
        self.check_scheme(object_identifiable)
        removed = self.get_transaction_template_retrying(self.get_max_retries()).execute(
            RemoveTransactionCallback(self, object_identifiable)
        )
        self.change_manager().entity_changed(ChangeType.REMOVED,
                                             removed.get_object_id(),
                                             removed.get_version_to_instant(),
                                             None,
                                             removed.get_version_to_instant())
        return removed

    def do_remove_in_transaction(self,
                                 object_identifiable):
        """
        Processes the document update, within a retrying transaction.
        @param objectIdentifiable the objectIdentifiable to remove, not null
        @return the updated document, not null
        """
        old_doc = self.get(object_identifiable=object_identifiable.get_object_id(),
                           version_correction=VersionCorrection.LATEST())
        if old_doc is None:
            raise DataNotFoundException('There is no document with oid:' + object_identifiable.get_object_id().__str__())
        now = self.now()
        old_doc.set_version_to_instant(now)
        self.update_version_to_instant(old_doc)
        return old_doc

    def correct(self, document):
        ArgumentChecker.not_null(document.get_unique_id(), 'document.unique_id')
        self.check_scheme(document.get_unique_id())
        before_id = document.get_unique_id()
        corrected = self.get_transaction_template_retrying(self.get_max_retries()).execute(
            CorrectTransactionCallback(self, before_id=before_id, document=document)
        )
        return corrected

    def do_correct_in_transaction(self, before_id, document):
        """
        Processes the document correction, within a retrying transaction.
        @param before_id  the ID before
        @param document  the document to correct, not null
        @return the corrected document, not null
        """
        old_doc = self.get_check_latest_correction(before_id)
        now = self.now()
        old_doc.set_correction_to_instant(now)
        self.update_correction_to_instant(old_doc)
        document.set_version_from_instant(old_doc.get_version_from_instant())
        document.set_version_to_instant(old_doc.get_version_to_instant())
        document.set_correction_from_instant(now) #old_doc.get_corrections_from_instant())
        document.set_correction_to_instant(None) #old_doc.get_corrections_to_instant())
        document.set_unique_id(old_doc.get_unique_id().to_latest())
        self.merge_non_updated_false(document, old_doc)
        self.insert(document)
        return document

    def merge_non_updated_false(self, document, old_document):
        pass

    def replace_version(self,
                        unique_id,
                        replacement_documents=None):
        now = self.now()
        return self.get_transaction_template_retrying(self.get_max_retries()).execute(
            ReplaceTransactionCallback(self, unique_id, now, replacement_documents)
        )

    def get_previous_document(self,
                              object_id,
                              now,
                              this_version_from):
        return self.history_by_versions_corrections(
            AbstractHistoryRequestPreviousDocument(self,
                                                   object_id=object_id,
                                                   corrected_to_instant=now,
                                                   version_instant=this_version_from
            )
        ).get_first_document()

    def get_all_current_documents(self,
                                  object_id,
                                  now):
        return self.history_by_versions_corrections(
            AbstractHistoryRequestAllCurrent(self,
                                             object_id,
                                             now
            )
        ).get_documents()

    def get_current_documents_in_range(self,
                                       object_id,
                                       now,
                                       instant_from,
                                       instant_to):
        return self.history_by_versions_corrections(
            AbstractHistoryRequestCurrentInRange(self,
                                                 object_id,
                                                 now,
                                                 instant_from,
                                                 instant_to

            )
        ).get_documents()

    def replace_all_versions(self,
                             object_id,
                             replacement_documents):
        now = dt.datetime.now()
        return self.get_transaction_template_retrying().execute(
            ReplaceAllTransactionCallback(self,
                                          object_id,
                                          now=now,
                                          replacement_documents=replacement_documents)
        )

    def replace_versions(self,
                         object_identifiable,
                         replacement_documents):
        now = self.now()
        if len(replacement_documents) > 0:
            ordered_replacement_documents = MasterUtils.adjust_version_instants(now,
                                                                                None,
                                                                                None,
                                                                                replacement_documents)
            lowest_versions_from = ordered_replacement_documents[0].get_version_from_instant()
            highest_version_to = ordered_replacement_documents[-1].get_version_to_instant()
            return self.get_transaction_template_retrying(self.get_max_retries()).execute(
                ReplaceVersionsTransactionCallback(self,
                                                   object_identifiable,
                                                   now,
                                                   replacement_documents,
                                                   ordered_replacement_documents,
                                                   lowest_versions_from,
                                                   highest_version_to)
            )
        else:
            return []

    def add_version(self,
                    object_identifiable,
                    document_to_add):
        result = self.replace_versions(object_identifiable,
                                       [document_to_add])
        if len(result) == 0:
            return None
        else:
            return result[0]

    def merge_none_updated_fields(self,
                                  new_document,
                                  old_document):
        """
        Merges any fields from the old document that have not been updated.
        Masters can choose to accept a null value for a field to mean
        @param newDocument  the new document to merge into, not null
        @param oldDocument  the old document to merge from, not null
        """
        pass

    def insert(self,
               document):
        """
        Inserts a new document.
        @param document  the document to insert, not null
        @return the new document, not null
        """
        pass

    def get_check_latest_version(self,
                                 unique_id):
        """
        Gets the document ensuring that it is the latest version.
        @param uniqueId  the unique identifier to load, not null
        @return the loaded document, not null

        """
        old_doc = self.get(unique_id)
        if old_doc.get_version_to_instant() is not None:
            raise Exception
        return old_doc

    def get_check_latest_correction(self,
                                    unique_id):
        old_doc = self.get(unique_id)
        if old_doc.get_correction_to_instant() is not None:
            raise TypeError('UniqueId is not latest correction: ' + unique_id.__str__())
        return old_doc

    def update_version_to_instant(self,
                                  document):
        """
        Updates the document row to mark the version as ended.
        @param document  the document to update, not null
        """
        args = DbMapSqlParameterSource()
        args.add_value('doc_id', self.extract_row_id(document.get_unique_id()))
        args.add_timestamp('ver_to_instant', document.get_version_to_instant())
        args.add_value('max_instant', DbDateUtils.MAX_SQL_TIMESTAMP)
        sql = self.get_sql_bundle().get_sql('UpdateVersionToInstant', args)
        odbc_ops = self.get_db_connector().get_odbc_template()
        rows_updated = odbc_ops.update(sql, args)
        if rows_updated != 1:
            raise Exception

    def check_latest_correction(self,
                                unique_id):
        """
        Gets the document ensuring that it is the latest version.
        @param uniqueId  the unique identifier to load, not null
        @return the loaded document, not null
        """
        old_doc = self.get(object_identifiable=unique_id)
        if old_doc.get_corrections_to_instant() is not None:
            raise TypeError('UniqueId is not latest correction: ' + unique_id.__str__())
        return old_doc

    def update_correction_to_instant(self,
                                     document):
        args = DbMapSqlParameterSource()
        args.add_value('doc_id', self.extract_row_id(document.get_unique_id()))
        args.add_timestamp('corr_to_instant', document.get_correction_to_instant())
        args.add_timestamp('max_instant', DbDateUtils.MAX_INSTANT())
        sql = self.get_sql_bundle().get_sql('UpdateCorrectionToInstant', args)
        odbc_ops = self.get_db_connector().get_odbc_template()
        rows_updated = odbc_ops.update(sql, args)
        if rows_updated != 1:
            raise Exception

    def get(self,
            unique_ids=None,
            object_identifiable=None,
            version_correction=None):
        """
        Queries the history of an object.
        @param request  the history request, not null
        @return the object history, not null
        @throws IllegalArgumentException if the request is invalid
        """
        if unique_ids:
            map_docs = dict()
            for unique_id in unique_ids:
                map_docs[unique_id] = self.get(object_identifiable=unique_id)
            return map_docs
        else:
            raise NotImplementedError()

    def history_by_versions_corrections(self,
                                       request):
        """
        Queries the history of an object.
        The request must contain an object identifier to identify the object.
        @param request  the history request, not null
        @return the object history, not null
        @throws TypeError if the request is invalid
        """
        pass


class ODBCQuery(object):
    def __init__(self,
                 qry_string,
                 wild_card_count,
                 wild_cards=None):
        self._qry_string = qry_string
        self._wild_card_count = wild_card_count
        self._wild_cards = dict()
        if wild_cards:
            assert(isinstance(wild_cards, dict))
            self._wild_cards = wild_cards

    @property
    def wild_cards(self):
        card_lst = []
        card_pt = 1
        while card_pt != 0:
            card_pt = self._qry_string.find('@', card_pt-1) + 1
            if card_pt == 0:
                break
            end_pt = self._qry_string[card_pt-1:].find(' ')
            if end_pt > 0:
                card_key = self._qry_string[card_pt-1:end_pt+card_pt-1]
                try:
                    card_value = self._wild_cards[card_key]
                except KeyError:
                    raise Exception
                card_lst.append(card_value)
        return card_lst

    @property
    def sql(self):
        return self._qry_string

    def add_card(self, key, card):
        self._wild_cards[key] = card


class TransactionCallback(object):
    def __init__(self,
                 call_back_func,
                 call_back_args):
        self._call_back = call_back_func
        self._args = call_back_args

    def call_back(self):
        return self._call_back(*self._args)