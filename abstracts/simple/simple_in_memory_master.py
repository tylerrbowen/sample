from ids.object_id_suppler import ObjectIdSupplier

__author__ = 'AH0137307'
import datetime as dt

from abstracts.abstract_master import AbstractMaster
from source.change_event_base import ChangeType
from source.change_manager_base import ChangeProvider, BasicChangeManager
from utils.master_utils import MasterUtils


class SimpleAbstractInMemoryMaster(AbstractMaster, ChangeProvider):
    DEFAULT_OID_SCHEME = 'MemSec'

    def __init__(self,
                 default_oid_scheme=None,
                 change_manager=None,
                 oid_supplier=None):
        super(SimpleAbstractInMemoryMaster, self).__init__()
        self._store = dict()
        if oid_supplier:
            self._object_id_supplier = oid_supplier
        else:
            self._object_id_supplier = ObjectIdSupplier(default_oid_scheme)
        if change_manager:
            self._change_manager = change_manager
        else:
            self._change_manager = BasicChangeManager()

    def replace_versions(self,
                         object_identifiable,
                         replacement_documents):
        return self.replace_all_versions(object_identifiable,
                                         replacement_documents)

    def replace_version(self,
                        document=None,
                        unique_id=None,
                        replacement_documents=None):
        if document:
            replacement_documents = [document]
        return self.replace_all_versions(unique_id.get_object_id(),
                                         replacement_documents)

    def replace_all_versions(self,
                             object_identifiable,
                             replacement_documents):
        for replacement_doc in replacement_documents:
            self.validate_document(replacement_doc)
        now = dt.datetime.now()
        stored_doc = self._store[object_identifiable.get_object_id()]
        if stored_doc is None:
            raise Exception
        if replacement_doc.is_empty():
            self._store.pop(object_identifiable.get_object_id())
            self._change_manager.entity_changed(ChangeType.REMOVED, object_identifiable.get_object_id(), None, None, now)
            return []
        else:
            stored_version_from = stored_doc.get_version_from_instant()
            stored_version_to = stored_doc.get_version_to_instant()
            ordered_replacement_docs = MasterUtils.adjust_version_instants(now,
                                                                           stored_version_from,
                                                                           stored_version_to,
                                                                           replacement_documents)
            last_replacement_doc = ordered_replacement_docs[-1]
            version_from_instant = ordered_replacement_docs[0].get_version_from_instant()
            version_to_instant = ordered_replacement_docs[-1].get_version_to_instant()
            self._change_manager.entity_changed(ChangeType.CHANGED,
                                                object_identifiable.get_object_id(),
                                                version_from_instant,
                                                version_to_instant,
                                                now)
            return tuple(last_replacement_doc,)

    def add_version(self,
                    object_identifiable,
                    document):
        result = self.replace_version(object_identifiable, [document])
        if result.is_empty():
            return None
        else:
            return result[0]

    def remove_version(self,
                       unique_id):
        self.replace_version(unique_id=unique_id,
                             replacement_documents=[])

    def get(self,
            unique_id=None,
            object_id=None,
            version_correction=None,
            unique_ids=None):
        result_map = dict()
        if unique_id:
            doc = self._store[unique_id.get_object_id()]
        elif object_id:
            doc = self._store[object_id.get_object_id()]
        elif unique_ids:
            for unique_id in unique_ids:
                doc = self.get(unique_id)
                result_map[unique_id] = doc
        return result_map
#
#
# class InMemorySecurityMaster(SimpleAbstractInMemoryMaster, SecurityMaster):
#     DEFAULT_OID_SCHEME = 'MemSec'
#
#     def __init__(self,
#                  default_oid_scheme=None,
#                  change_manager=None,
#                  oid_supplier=None):
#         super(InMemorySecurityMaster, self).__init__(default_oid_scheme,
#                                                      change_manager,
#                                                      oid_supplier)
#
#     def search(self, request):
#         lst = []
#         for doc in self._store.values():
#             if request.matches(doc):
#                 lst.append(doc)
#         sorted(lst, reverse=request.get_sort_order())
#         result = SecuritySearchResult()
#         result.set_paging(Paging.of(request.get_paging_request()), lst)
#         result.get_documents().add_all(request.get_paging_request().select(lst))
#         return result
#
#     def get(self,
#             unique_id=None,
#             object_id=None,
#             version_correction=None,
#             bundle=None,
#             unique_ids=None):
#         if unique_id:
#             if not version_correction:
#                 return self.get(unique_id=unique_id, version_correction=VersionCorrection.LATEST())
#             else:
#                 document = self._store.get(unique_id.get_object_id())
#                 if document is None:
#                     raise Exception
#                 return document
#         if object_id:
#             if not version_correction:
#                 return self.get(object_id=object_id, version_correction=VersionCorrection.LATEST())
#             else:
#                 document = self._store.get(object_id)
#                 if document is None:
#                     raise Exception
#                 return document
#
#     def add(self, document):
#         object_id = self._object_id_supplier.get()
#         unique_id = object_id.at_version('')
#         security = document.get_security()
#         security.set_unique_id(unique_id)
#         now = dt.datetime.now()
#         doc = SecurityDocument(security=security)
#         doc.set_version_from_instant(now)
#         doc.set_version_to_instant(now)
#         self._store[object_id] = doc
#         self._change_manager.entity_changed(ChangeType.ADDED, object_id,
#                                             doc.get_version_from_instant(),
#                                             doc.get_version_to_instant(),
#                                             now)
#         return doc
#
#     def update(self, document):
#         unique_id = document.get_unique_id()
#         now = dt.datetime.now()
#         stored_document = self._store.get(unique_id.get_object_id())
#         if stored_document is None:
#             raise Exception
#         document.set_version_from_instant(now)
#         document.set_version_to_instant(None)
#         document.set_correction_from_instant(now)
#         document.set_correction_to_instant(None)
#         self._store[unique_id.get_object_id()] = document
#         self._change_manager.entity_changed(ChangeType.CHANGED,
#                                             unique_id.get_object_id(),
#                                             stored_document.get_version_from_instant(),
#                                             document.get_version_to_instant(),
#                                             now)
#         return document
#
#     def remove(self, object_identifiable):
#         super(InMemorySecurityMaster, self).remove(object_identifiable)
#
#     def correct(self, document):
#         return self.update(document)
#
#     def history(self, request):
#         super(InMemorySecurityMaster, self).history(request)











