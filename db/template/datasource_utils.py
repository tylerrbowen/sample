from connection_holder import ConnectionHolder
from db.template.transaction.transaction_synchronization_manager import TransactionSynchronizationManager
from transaction.transaction_definition import TransactionDefinition

class DataSourceUtils(object):

    @classmethod
    def get_connection(cls, data_source):
        try:
            return cls.do_get_connection(data_source)
        except Exception, ex:
            raise Exception('Could not get Exception', ex)

    @classmethod
    def do_get_connection(cls, data_source):
        con_holder = TransactionSynchronizationManager.get_resource(data_source)
        if con_holder is not None and con_holder.has_connection():
            #con_holder.request()
            if not con_holder.has_connection():
                con_holder.set_connection(data_source.get_connection())
            return con_holder.get_connection()

        con = data_source.get_connection()
        holder_to_use = ConnectionHolder(con)
        holder_to_use.requested()
        #TransactionSynchronizationManager.bind_resource(data_source, holder_to_use)
        return con

    @classmethod
    def release_connection(cls, con, data_source):
        """
        con: Connection
        data_source: DataSource
        """
        if con is None:
            return
        if data_source is not None:
            con_holder = TransactionSynchronizationManager.get_resource(data_source)
            if con_holder is not None:
                con_holder.released()
                return
        cls.close_connection(con, data_source)

    @classmethod
    def reset_connection_after_transaction(cls, con, previous_isolation_level):
        try:
            if previous_isolation_level is not None:
                con.set_transaction_isolation(previous_isolation_level)
            if con.is_read_only():
                con.set_read_only(False)
        except Exception, ex:
            print ex.message

    @classmethod
    def prepare_connection_for_transaction(cls, con, definition):
        """
        Prepare the given Connection with the given transaction semantics.
        @param con the Connection to prepare
        @param definition the transaction definition to apply
        @return the previous isolation level, if any
        """
        if definition is not None and definition.is_read_only():
            try:
                con.set_read_only(True)
            except Exception, ex:
                print ex.message

        previous_isolation_level = None
        if definition is not None and definition.get_isolation_level() != TransactionDefinition.ISOLATION_DEFAULT:
            current_isolation = con.get_transaction_isolation()
            if current_isolation != definition.get_isolation_level():
                previous_isolation_level = current_isolation
                con.set_transaction_isolation(definition.get_isolation_level())
        return previous_isolation_level


    @classmethod
    def close_connection(cls, con, data_source):
        con.close()
        return
