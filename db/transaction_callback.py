from utils.exceptions.data_not_found_exception import DataNotFoundException
from utils.master_utils import MasterUtils
from source.change_event_base import ChangeType


class TransactionCallback(object):
    def __init__(self, caller):
        self._caller = caller

    def do_in_transaction(self, transaction_status):
        pass


class AddTransactionCallback(TransactionCallback):
    def __init__(self, caller, document):
        super(AddTransactionCallback, self).__init__(caller)
        self._doc = document

    def do_in_transaction(self, transaction_status):
        return self._caller.do_add_in_transaction(self._doc)


class UpdateTransactionCallback(TransactionCallback):
    def __init__(self, caller, before_id, document):
        super(UpdateTransactionCallback, self).__init__(caller)
        self._before_id = before_id
        self._doc = document

    def do_in_transaction(self, transaction_status):
        return self._caller.do_update_in_transaction(self._before_id, self._doc)


class RemoveTransactionCallback(TransactionCallback):
    def __init__(self, caller, object_identifiable):
        super(RemoveTransactionCallback, self).__init__(caller)
        self._object_identifiable = object_identifiable

    def do_in_transaction(self, transaction_status):
        return self._caller.do_remove_in_transaction(self._object_identifiable)


class CorrectTransactionCallback(TransactionCallback):

    def __init__(self, caller, before_id, document):
        super(CorrectTransactionCallback, self).__init__(caller)
        self._before_id = before_id
        self._doc = document

    def do_in_transaction(self, transaction_status):
        return self._caller.do_correct_in_transaction(self._before_id, self._doc)


class ReplaceTransactionCallback(TransactionCallback):
    def __init__(self, caller, unique_id, now, replacement_documents):
        super(ReplaceTransactionCallback, self).__init__(caller)
        self._unique_id = unique_id
        self._call_now = now
        self._replacement_documents = replacement_documents

    def do_in_transaction(self, transaction_status):
        stored_document = self._caller.get(object_identifiable=self._unique_id)
        if stored_document is None:
            raise DataNotFoundException('Document not found: ' + self._unique_id.__str__())
        stored_version_from = stored_document.get_version_from_instant()
        stored_version_to = stored_document.get_version_to_instant()
        now = self._call_now
        stored_document.set_correction_to_instant(now)
        self._caller.update_correction_to_instant(stored_document)
        ordered_replacement_documents = MasterUtils.adjust_version_instants(now,
                                                                            stored_version_from,
                                                                            stored_version_to,
                                                                            self._replacement_documents)
        new_versions = []
        if len(ordered_replacement_documents) == 0:
            previous_document = self._caller.get_previous_document(self._unique_id.get_object_id(), now, stored_version_from)
            if previous_document:
                previous_document.set_correction_to_instant(now)
                self._caller.update_correction_to_instant(previous_document)
                previous_document.set_correction_from_instant(now)
                previous_document.set_correction_to_instant(None)
                previous_document.set_version_to_instant(stored_version_from)
                previous_document.set_unique_id(self._unique_id.get_unique_id().to_latest())
                self._caller.insert(previous_document)
                new_versions.append(previous_document)
                self._caller.get_change_manager().entity_changed(ChangeType.CHANGED,
                                                                 stored_document.get_object_id(),
                                                                 stored_version_from,
                                                                 stored_version_to,
                                                                 now)
            else:
                self._caller.get_change_manager().entity_changed(ChangeType.REMOVED,
                                                                 stored_document.get_object_id(),
                                                                 None,
                                                                 None,
                                                                 now)
        else:
            for replacement_document in ordered_replacement_documents:
                replacement_document.set_unique_id(self._unique_id.get_unique_id().to_latest())
                self._caller.insert(replacement_document)
                new_versions.append(replacement_document)
            self._caller.get_change_manager().entity_changed(ChangeType.CHANGED,
                                                             stored_document.get_object_id(),
                                                             stored_version_from,
                                                             stored_version_to,
                                                             now)
        return MasterUtils.map_to_unique_ids(new_versions)


class ReplaceAllTransactionCallback(TransactionCallback):
    def __init__(self,
                 caller,
                 object_id,
                 now,
                 replacement_documents):
        super(ReplaceAllTransactionCallback, self).__init__(caller)
        self._call_id = object_id
        self._call_now = now
        self._call_replacement_documents = replacement_documents

    def do_in_transaction(self, transaction_status):
        terminated_any = False
        stored_documents = self._caller.get_all_current_documents(self._call_id.get_object_id(),
                                                                  self._call_now)
        # if not len(stored_documents) == 0:
        #     earliest_stored_document = stored_documents[-1]
        #     latest_stored_document = stored_documents[0]
        #     for stored_document in stored_documents:
        #         stored_document.set_correction_to_instant(self._call_now)
        #         self._caller.update_correction_to_instant(stored_document)
        #         terminated_any = False
        #     if earliest_stored_document is not None and earliest_stored_document.get_version_from_instant().is_before(self.
        #     )

        for stored_document in stored_documents:
            stored_document.set_correction_to_instant(self._call_now)
            self._caller.update_correction_to_instant(stored_document)
            terminated_any = True

        if terminated_any and len(self._call_replacement_documents) == 0:
            self._caller.get_change_manager().entity_changed(ChangeType.REMOVED(),
                                                             self._call_id.get_object_id(),
                                                             None,
                                                             None,
                                                             self._call_now)
            return []
        else:
            ordered_replacement_documents = MasterUtils.adjust_version_instants(self._call_now, None, None, self._call_replacement_documents)
            for replacement_document in ordered_replacement_documents:
                replacement_document.set_unique_id(self._call_id.get_object_id().at_latest_version())
                self._caller.insert(replacement_document)
            version_from_instant = ordered_replacement_documents[0].get_version_from_instant()
            version_to_instant = ordered_replacement_documents[-1].get_version_to_instant()
            self._caller.get_change_manager().entity_changed(ChangeType.CHANGED(),
                                                             self._call_id.get_object_id(),
                                                             version_from_instant,
                                                             version_to_instant,
                                                             self._call_now)
            return MasterUtils.map_to_unique_ids(ordered_replacement_documents)



class ReplaceVersionsTransactionCallback(TransactionCallback):
    def __init__(self,
                 caller,
                 object_id,
                 now,
                 replacement_documents,
                 ordered_replacement_documents,
                 lowest_version_from,
                 highest_version_to):
        super(ReplaceVersionsTransactionCallback, self).__init__(caller)
        self._call_id = object_id
        self._call_now = now
        self._call_replacement_documents = replacement_documents
        self._call_ordered_replacement_documents = ordered_replacement_documents
        self._call_lowest_version_from = lowest_version_from
        self._call_highest_version_to = highest_version_to

    def do_in_transaction(self, transaction_status):
        terminated_any = False
        stored_documents = self._caller.get_current_documents_in_range(self._call_id.get_object_id(),
                                                                       self._call_now,
                                                                       self._call_lowest_version_from,
                                                                       self._call_highest_version_to)
        if not len(stored_documents) == 0:
            earliest_stored_document = stored_documents[-1]
            latest_stored_document = stored_documents[0]
            for stored_document in stored_documents:
                stored_document.set_correction_to_instant(self._call_now)
                self._caller.update_correction_to_instant(stored_document)
                terminated_any = True
            if earliest_stored_document is not None \
                    and earliest_stored_document.get_version_from_instant().is_before(self._call_lowest_version_from):
                earliest_stored_document.set_version_to_instant(self._call_lowest_version_from)
                earliest_stored_document.set_correction_from_instant(self._call_now)
                earliest_stored_document.set_correction_to_instant(None)
                earliest_stored_document.set_unique_id(self._call_id.get_object_id().at_latest_version())
                self._caller.insert(earliest_stored_document)

            if latest_stored_document is not None and \
                    latest_stored_document.get_version_to_instant() is not None and \
                    self._call_highest_version_to is not None and \
                    latest_stored_document.get_version_to_instant().is_after(self._call_highest_version_to):
                latest_stored_document.set_version_from_instant(self._call_highest_version_to)
                latest_stored_document.set_correction_from_instant(self._call_now)
                latest_stored_document.set_correction_to_instant(None)
                latest_stored_document.set_unique_id(self._call_id.get_object_id().at_latest_version())
                self._caller.insert(latest_stored_document)

        if terminated_any and len(self._call_replacement_documents) == 0:
            self._caller.get_change_manager().entity_changed(ChangeType.REMOVED(),
                                                             self._call_id.get_object_id(),
                                                             None,
                                                             None,
                                                             self._call_now)
            return []
        else:
            for replacement_document in self._call_ordered_replacement_documents:
                replacement_document.set_unique_id(self._call_id.get_object_id().at_latest_version())
                self._caller.insert(replacement_document)
            version_from_instant = self._call_ordered_replacement_documents[0].get_version_from_instant()
            version_to_instant = self._call_ordered_replacement_documents[-1].get_version_to_instant()
            self._caller.get_change_manager().entity_changed(ChangeType.CHANGED(),
                                                             self._call_id.get_object_id(),
                                                             version_from_instant,
                                                             version_to_instant,
                                                             self._call_now)
            return MasterUtils.map_to_unique_ids(self._call_ordered_replacement_documents)



class HTSUpdateTransactionCallback(TransactionCallback):
    def __init__(self,
                 caller,
                 unique_id,
                 series):
        super(HTSUpdateTransactionCallback, self).__init__(caller)
        self._unique_id = unique_id
        self._series = series

    def do_in_transaction(self, transaction_status):
        now = self._caller.now()
        self._caller.insert_data_points_check_max_data(self._caller._unique_id, self._caller._series)
        return (self._caller.insert(self._unique_id, self._series, now), now)



class HTSCorrectTransactionCallback(TransactionCallback):
    def __init__(self,
                 caller,
                 unique_id,
                 series):
        super(HTSCorrectTransactionCallback, self).__init__(caller)
        self._unique_id = unique_id
        self._series = series

    def do_in_transaction(self, transaction_status):
        now = self._caller.now()
        return (self._caller.correct_data_points(self._unique_id, self._series, now), now)


class HTSRemoveTransactionCallback(TransactionCallback):
    def __init__(self,
                 caller,
                 unique_id,
                 from_date_inclusive,
                 to_date_inclusive):
        super(HTSRemoveTransactionCallback, self).__init__(caller)
        self._unique_id = unique_id
        self._from_date_inclusive = from_date_inclusive
        self._to_date_inclusive = to_date_inclusive

    def do_in_transaction(self, transaction_status):
        now = self._caller.now()
        return (self._caller.remove_data_points(
            self._caller._unique_id,
            self._from_date_inclusive,
            self._to_date_inclusive,
            now),
                now)



