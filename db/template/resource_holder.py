import datetime as dt
import numpy as np


class ResourceHolder(object):
    """
    Generic interface to be implemented by resource holders.
    """
    def reset(self):
        """
        Reset the transactional state of this holder.
        """
        pass

    def unbound(self):
        """
        Notify this holder that it has been unbound from transaction synchronization.
        """
        pass

    def is_void(self):
        """
        Determine whether this holder is considered as 'void',
        """
        pass


class ResourceHolderSupport(ResourceHolder):
    """
    Convenient base class for resource holders.
     Features rollback-only support for nested transactions.
     * Can expire after a certain number of seconds or milliseconds,
     * to determine transactional timeouts.
    """
    def __init__(self):
        super(ResourceHolder, self).__init__()
        self._synchronized_with_transaction = False
        self._rollback_only = False
        self._deadline = None
        self._reference_count = 0
        self._is_void = False

    def reset(self):
        self.clear()
        self._reference_count = 0

    def unbound(self):
        self._is_void = True

    def is_void(self):
        return self._is_void

    def set_synchronized_with_transaction(self, synchronized_with_transaction):
        """
        Mark the resource as synchronized with a transaction.
        """
        self._synchronized_with_transaction = synchronized_with_transaction

    def is_synchronized_with_transaction(self):
        """
        Return whether the resource is synchronized with a transaction.
        """
        return self._synchronized_with_transaction

    def set_rollback_only(self):
        """
        Mark the resource transaction as rollback-only.
        """
        self._rollback_only = True

    def is_rollback_only(self):
        """
        Return whether the resource transaction is marked as rollback-only.
        """
        return self._rollback_only

    def set_timeout_in_seconds(self, seconds):
        """
        Set the timeout for this object in seconds.
        """
        self.set_timeout_in_millis(seconds * 1000)

    def set_timeout_in_millis(self, millis):
        """
        Set the timeout for this object in milliseconds.
        """
        self._deadline = dt.datetime.now() + dt.timedelta(days=0, seconds=0, microseconds=millis * 1000)

    def has_timeout(self):
        """
        * Return whether this object has an associated timeout.
        """
        return self._deadline is not None

    def get_deadline(self):
        """
        Return the expiration deadline of this object.
        """
        return self._deadline

    def requested(self):
        self._reference_count += 1

    def released(self):
        self._reference_count -= 1

    def is_open(self):
        return self._reference_count > 0

    def clear(self):
        self._synchronized_with_transaction = False
        self._rollback_only = False
        self._deadline = None

    def get_time_to_live_in_seconds(self):
        """
        Return the time to live for this object in seconds.
        Rounds up eagerly, e.g. 9.00001 still to 10.
        """
        diff = int(self.get_time_to_live_in_millis()/1000)
        secs = int(np.ceil(diff))
        self.check_transaction_timeout(secs <= 0)
        return secs

    def get_time_to_live_in_millis(self):
        """
        * Return the time to live for this object in milliseconds.
        """
        if self._deadline is None:
            raise TypeError
        time_to_live = int((self._deadline - dt.datetime.now()).total_seconds()*1000)
        self.check_transaction_timeout(time_to_live < 0)
        return time_to_live

    def check_transaction_timeout(self, deadline_reached):
        """
        * Set the transaction rollback-only if the deadline has been reached,
        * and throw a TransactionTimedOutException.
        """
        if deadline_reached:
            self.set_rollback_only()
            raise Exception('Transaction timed out')


