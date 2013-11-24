class TransactionSynchronizationManager(object):
    """
    Central helper that manages resources and transaction synchronizations per thread.
    Supports one resource per key without overwriting

    """
    resources = dict()
    synchronizations = set()
    current_transaction_name = ''
    current_transaction_read_only = bool
    current_transaction_isolation_level = int
    actual_transaction_active = bool

    @classmethod
    def get_resource_map(cls):
        """
        Return all resources that are bound to the current thread.
        """
        return cls.resources

    @classmethod
    def has_resource(cls, key):
        """
        Check if there is a resource for the given key bound to the current thread.
        """
        value = cls.resources.get(key)
        return value is not None

    @classmethod
    def get_resource(cls, key):
        """
        Retrieve a resource for the given key that is bound to the current thread.
        """
        resource = cls.resources.get(key)
        return resource

    @classmethod
    def bind_resource(cls, key, resource):
        """
        Bind the given resource for the given key to the current thread.
        """
        cls.resources[key] = resource

    @classmethod
    def unbind_resource(cls, key):
        """
        Unbind a resource for the given key from the current thread.
        """
        try:
            popped = cls.resources.pop(key)
        except KeyError:
            popped = None
        return popped

    @classmethod
    def is_synchronization_active(cls):
        """
        Return if transaction synchronization is active for the current thread.
        """
        return len(cls.synchronizations) > 0

    @classmethod
    def init_synchronization(cls):
        """
        Activate transaction synchronization for the current thread.
        """
        cls.synchronizations = set()

    @classmethod
    def register_synchronization(cls, synchronization):
        """
        Register a new transaction synchronization for the current thread.
        TransactionSynchronization: synchronization
        """
        cls.synchronizations.add(synchronization)

    @classmethod
    def get_synchronizations(cls):
        """
        Return an unmodifiable snapshot list of all registered synchronizations

        """
        synchs = cls.synchronizations
        if synchs is None:
            raise Exception("Transaction synchronization is not active")
        if len(synchs) == 0:
            return []
        else:
            sorted_synchs = list(synchs)
            sorted_synchs.sort()
            return sorted_synchs

    @classmethod
    def clear_synchronization(cls):
        """
        Deactivate transaction synchronization for the current thread.
        """
        cls.synchronizations.clear()

    @classmethod
    def set_current_transaction_name(cls, name):
        """
        Expose the name of the current transaction, if any.
        """
        cls.current_transaction_name = name

    @classmethod
    def get_current_transaction_name(cls):
        """
        Return the name of the current transaction, or {@code null} if none set.
        """
        return cls.current_transaction_name

    @classmethod
    def set_current_transaction_read_only(cls, read_only):
        """
        Expose a read-only flag for the current transaction.
        """
        cls.current_transaction_read_only = read_only

    @classmethod
    def is_current_transaction_read_only(cls):
        """
        Return whether the current transaction is marked as read-only.
        To be called by resource management code when preparing a newly
        """
        return cls.current_transaction_read_only

    @classmethod
    def get_current_transaction_isolation_level(cls):
        """
        Expose an isolation level for the current transaction.
        """
        return cls.current_transaction_isolation_level

    @classmethod
    def set_current_transaction_isolation_level(cls, isolation_level):
        """
        Return the isolation level for the current transaction, if any.
        """
        cls.current_transaction_isolation_level = isolation_level

    @classmethod
    def set_actual_transaction_active(cls, active):
        """
        Expose whether there currently is an actual transaction active.
        """
        cls.actual_transaction_active = active

    @classmethod
    def get_actual_transaction_active(cls):
        """
        Return whether there currently is an actual transaction active.
        """
        return cls.actual_transaction_active

    @classmethod
    def clear(cls):
        """
        Clear the entire transaction synchronization state for the current thread:
        """
        cls.clear_synchronization()
        cls.set_current_transaction_name(None)
        cls.set_current_transaction_read_only(None)
        cls.set_actual_transaction_active(None)
        cls.set_current_transaction_isolation_level(None)