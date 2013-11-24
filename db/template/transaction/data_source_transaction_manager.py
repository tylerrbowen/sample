from db.template.transaction.transaction_synchronization_manager import TransactionSynchronizationManager
from platform_transaction_manager import AbstractPlatformTransactionManager
from db.template.datasource_utils import DataSourceUtils
from transaction_object import ODBCTransactionObject
from db.template.connection_holder import ConnectionHolder
from transaction_definition import TransactionDefinition


class DataSourceTransactionManager(AbstractPlatformTransactionManager):
    def __init__(self,
                 data_source=None):
        super(DataSourceTransactionManager, self).__init__()
        self._data_source = data_source
        self.set_data_source(data_source)
        self.after_properties_set()

    def set_data_source(self, data_source):
        self._data_source = data_source

    def after_properties_set(self):
        if self.get_data_source() is None:
            raise Exception

    def get_data_source(self):
        return self._data_source

    def get_resource_factory(self):
        return self._data_source

    def do_get_transaction(self):
        tx_object = DataSourceTransactionObject(self)
        con_holder = TransactionSynchronizationManager.get_resource(self._data_source)
        if con_holder is None:
            new_con = self._data_source.get_connection()
            tx_object.set_connection_holder(ConnectionHolder(connection=new_con), True)
            TransactionSynchronizationManager.bind_resource(self._data_source, tx_object.get_connection_holder())
            con_holder = TransactionSynchronizationManager.get_resource(self._data_source)
        tx_object.set_connection_holder(con_holder, False)
        return tx_object

    def is_existing_transaction(self, transaction):
        tx_object = transaction
        return tx_object.get_connection_holder() is not None and \
               tx_object.get_connection_holder().is_transaction_active()

    def do_begin(self, transaction, definition):
        tx_object = transaction
        con = None
        try:
            if tx_object.get_connection_holder() is None or \
                    tx_object.get_connection_holder().is_synchronized_with_transaction():
                new_con = self._data_source.get_connection()
                tx_object.set_connection_holder(ConnectionHolder(new_con), True)
            tx_object.get_connection_holder().set_synchronized_with_transaction(True)
            con = tx_object.get_connection_holder().get_connection()

            previous_isolation_level = DataSourceUtils.prepare_connection_for_transaction(con, definition)
            tx_object.set_previous_isolation_level(previous_isolation_level)

            if con.autocommit:
                tx_object.set_must_restore_auto_commit(True)
                timeout = self.determine_timeout(definition)
                if timeout is not TransactionDefinition.TIMEOUT_DEFAULT:
                    tx_object.get_connection_holder().set_timeout_in_seconds(timeout)
                if tx_object.is_new_connection_holder():
                    TransactionSynchronizationManager.bind_resource(self.get_data_source(),
                                                                    tx_object.get_connection_holder())
            tx_object.get_connection_holder().set_transaction_active(True)

        except Exception, ex:
            DataSourceUtils.release_connection(con, self._data_source)
            raise Exception('Couldn\'t do it')

    def do_suspend(self, transaction):
        tx_object = transaction
        try:
            tx_object.set_connection_holder(None)
            con_holder = TransactionSynchronizationManager.unbind_resource(self._data_source)
            return con_holder
        except AttributeError:
            return None


    def do_resume(self, transaction, suspended_resources):
        con_holder = suspended_resources
        TransactionSynchronizationManager.bind_resource(self._data_source, con_holder)

    def do_commit(self, status):
        tx_object = status.get_transaction()
        con = tx_object.get_connection_holder().get_connection()
        try:
            con.commit()
        except Exception, e:
            raise Exception("Could not commit", e)

    def do_rollback(self, status):
        tx_object = status.get_transaction()
        con = tx_object.get_connection_holder().get_connection()
        try:
            con.rollback()
        except Exception, e:
            raise Exception('could not roll back', e)

    def do_set_rollback_only(self, status):
        tx_object = status.get_transaction()
        tx_object.set_rollback_only()

    def do_cleanup_after_completion(self, transaction):
        tx_object = transaction
        if tx_object.is_new_connection_holder():
            TransactionSynchronizationManager.unbind_resource(self._data_source)
        con = tx_object.get_connection_holder().get_connection()
        try:
            if tx_object.is_must_restore_auto_commit():
                con.set_auto_commit(True)
            DataSourceUtils.reset_connection_after_transaction(con, tx_object.get_previous_isolation_level())
        except Exception, e:
            pass
        if tx_object.is_new_connection_holder():
            DataSourceUtils.release_connection(con, self._data_source)
        tx_object.get_connection_holder().clear()


class DataSourceTransactionObject(ODBCTransactionObject):
    def __init__(self, caller):
        super(DataSourceTransactionObject, self).__init__()
        self._new_connection_holder = False
        self._must_restore_auto_commit = False
        self._caller = caller

    def set_connection_holder(self, connection_holder, new_holder):
        super(DataSourceTransactionObject, self).set_connection_holder(connection_holder)
        self._new_connection_holder = new_holder

    def is_new_connection_holder(self):
        return self._new_connection_holder

    def set_must_restore_auto_commit(self, commit):
        self._must_restore_auto_commit = commit

    def is_must_restore_auto_commit(self):
        return self._must_restore_auto_commit

    def set_rollback_only(self):
        self._caller.get_connection_holder().set_rollback_only()

    def is_rollback_only(self):
        return self._caller.get_connection_holder().is_rollback_only()






