from db.template.transaction.transaction_synchronization_manager import TransactionSynchronizationManager


class TransactionSynchronization(object):
    """
    Interface for transaction synchronization callbacks.
    TransactionSynchronization implementations can implement the Ordered interface
    to influence their execution order. A synchronization that does not implement the
    Ordered interface is appended to the end of the synchronization chain.
    """
    def __init__(self):
        """
        STATUS_COMMITTED: Completion status in case of proper commit
        STATUS_ROLLED_BACK: Completion status in case of proper rollback
        STATUS_UNKNOWN: Completion status in case of heuristic mixed completion or system errors

        """
        self.STATUS_COMMITTED = 0
        self.STATUS_ROLLED_BACK = 1
        self.STATUS_UNKNOWN = 2

    def suspend(self):
        """
        Suspend this synchronization.
        """
        pass

    def resume(self):
        """
        Resume this synchronization.
        """
        pass

    def flush(self):
        """
        Flush the underlying session to the datastore, if applicable:
        """
        pass

    def before_commit(self, read_only):
        """
        Invoked before transaction commit (before "beforeCompletion").
        """
        pass

    def before_completion(self):
        """
        Invoked before transaction commit/rollback.
        """
        pass

    def after_commit(self):
        """
        Invoked after transaction commit. Can perform further operations right
        """
        pass

    def after_completion(self, status):
        """
        Invoked after transaction commit/rollback.
        """
        pass


class ResourceHolderSynchronization(TransactionSynchronization):

    def __init__(self,
                 resource_holder,
                 resource_key):
        super(ResourceHolderSynchronization, self).__init__()
        self._resource_holder = resource_holder
        self._resource_key = resource_key
        self._holder_active = True

    def suspend(self):
        if self._holder_active:
            TransactionSynchronizationManager.unbind_resource(self._resource_key)

    def resume(self):
        if self._holder_active:
            TransactionSynchronizationManager.bind_resource(self._resource_key, self._resource_holder)

    def flush(self):
        self.flush_resource(self._resource_holder)

    def before_commit(self, read_only):
        pass

    def before_completion(self):
        if self.should_unbind_at_completion():
            TransactionSynchronizationManager.unbind_resource(self._resource_key)
            self._holder_active = False
            if self.should_release_before_completion():
                self.release_resource(self._resource_holder, self._resource_key)

    def after_completion(self, status):
        if self.should_unbind_at_completion():
            if self._holder_active:
                self._holder_active = False
                TransactionSynchronizationManager.unbind_resource(self._resource_key)
                self._resource_holder.unbound()
                release_necessary = True
            else:
                release_necessary = self.should_release_after_completion(self._resource_holder)
            if release_necessary:
                self.release_resource(self._resource_holder, self._resource_key)
        else:
            self.cleanup_resource(self._resource_holder, self._resource_key, (status == self.STATUS_COMMITTED))
        self._resource_holder.reset()

    def should_unbind_at_completion(self):
        return True

    def should_release_before_completion(self):
        return True

    def should_release_after_completion(self, resource_holder):
        pass

    def flush_resource(self, resource_holder):
        pass

    def process_resource_after_commit(self):
        pass

    def release_resource(self, resource_holder, resource_key):
        pass

    def cleanup_resource(self, resource_holder, resource_key, committed):
        pass