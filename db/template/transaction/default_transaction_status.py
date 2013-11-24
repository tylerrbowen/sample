

from abc import ABCMeta, abstractmethod, abstractproperty

class TransactionStatus(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_new_transaction(self):
        """
        Return whether the present transaction is new (else participating
        in an existing transaction, or potentially not running in an
        actual transaction in the first place).
        """
        pass

    @abstractmethod
    def has_savepoint(self):
        """
        Return whether this transaction internally carries a savepoint,
        that is, has been created as nested transaction based on a savepoint.
        """
        pass

    @abstractmethod
    def is_rollback_only(self):
        """
        Return whether the transaction has been marked as rollback-only
        (either by the application or by the transaction infrastructure).
        """
        pass

    @abstractmethod
    def set_rollback_only(self):
        """
        Set the transaction rollback-only. This instructs the transaction manager
        that the only possible outcome of the transaction may be a rollback, as
        alternative to throwing an exception which would in turn trigger a rollback.
        """
        pass

    @abstractmethod
    def flush(self):
        """
        flush the underlying session
        """
        pass

    def is_completed(self):
        """
        Return whether this transaction is completed, that is,
        whether it has already been committed or rolled back.
        """
        pass


class AbstractTransactionStatus(TransactionStatus):

    def __init__(self):
        self._rollback_only = False
        self._completed = False
        self._savepoint = None

    def set_rollback_only(self):
        self._rollback_only = True

    def is_rollback_only(self):
        return self.is_local_rollback_only() or self.is_global_rollback_only()

    def is_local_rollback_only(self):
        return self._rollback_only

    def is_global_rollback_only(self):
        return False

    def flush(self):
        pass

    def set_completed(self):
        self._completed = True

    def is_completed(self):
        return self._completed

    def set_savepoint(self, savepoint):
        self._savepoint = savepoint

    def get_savepoint(self):
        return self._savepoint

    def has_savepoint(self):
        return self._savepoint is not None

    def create_and_hold_savepoint(self):
        pass

    def rollback_to_held_savepoint(self):
        pass

    def release_held_savepoint(self):
        pass

    def create_savepoint(self):
        pass

    def rollback_to_savepoint(self, savepoint):
        pass

    def release_savepoint(self, savepoint):
        pass

    def get_savepoint_manager(self):
        pass


class DefaultTransactionStatus(AbstractTransactionStatus):
    """
    Default implementation of the {@link org.springframework.transaction.TransactionStatus}
    interface, used by {@link AbstractPlatformTransactionManager}. Based on the concept
    of an underlying "transaction object".
    <p>Holds all status information that {@link AbstractPlatformTransactionManager}
    needs internally, including a generic transaction object determined by the
    concrete transaction manager implementation.
    <p>Supports delegating savepoint-related methods to a transaction object
    that implements the {@link SavepointManager} interface.
    <p><b>NOTE:</b> This is <i>not</i> intended for use with other PlatformTransactionManager
    implementations, in particular not for mock transaction managers in testing environments.
    Use the alternative {@link SimpleTransactionStatus} class or a mock for the plain
    {@link org.springframework.transaction.TransactionStatus} interface instead.

    """
    def __init__(self,
                 transaction,
                 new_transaction,
                 new_synchronization,
                 read_only,
                 suspended_resources):
        super(AbstractTransactionStatus, self).__init__()
        self._transaction = transaction
        self._new_transaction = new_transaction
        self._new_synchronization = new_synchronization
        self._read_only = read_only
        self._suspended_resources = suspended_resources

    def get_transaction(self):
        return self._transaction

    def has_transaction(self):
        return self._transaction is not None

    def is_new_transaction(self):
        return self.has_transaction() and self._new_transaction

    def is_new_synchronization(self):
        return self._new_synchronization

    def is_read_only(self):
        return self._read_only

    def get_suspended_resources(self):
        return self._suspended_resources











