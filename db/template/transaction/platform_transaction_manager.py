from transaction_definition import TransactionDefinition
from default_transaction_defintion import DefaultTransactionDefinition
from default_transaction_status import DefaultTransactionStatus


class PlatformTransactionManager(object):
    """
    This is the central interface in Spring's transaction infrastructure.
    """
    def get_transaction(self, definition):
        """
        Return a currently active transaction or create a new one, according to
        the specified propagation behavior.
        definition: TransactionDefinition
        """
        pass

    def commit(self, status):
        """
        Commit the given transaction, with regard to its status.
        status: TransactionStatus
        """
        pass

    def rollback(self, status):
        """
        status: TransactionStatus

        Perform a rollback of the given transaction.

        """
        pass


class AbstractPlatformTransactionManager(PlatformTransactionManager):
    SYNCHRONIZATION_ALWAYS = 0
    SYNCHRONIZATION_ON_ACTUAL_TRANSACTION = 1
    SYNCHRONIZATION_NEVER = 2

    def __init__(self):
        self._transaction_synchronization = self.SYNCHRONIZATION_NEVER
        self._default_timeout = TransactionDefinition.TIMEOUT_DEFAULT
        self._nested_transaction_allowed = False
        self._validated_existing_transaction = False
        self._global_rollback_on_participation_failure = True
        self._fail_early_on_global_rollback_only = False
        self._rollback_on_commit_failure = False

    def set_transaction_synchronization_name(self, constant_name):
        constant_int = self.__dict__.get(constant_name)
        if constant_int is None:
            raise Exception
        self.set_transaction_synchronization(constant_int)

    def set_transaction_synchronization(self, constant_int):
        self._transaction_synchronization = constant_int

    def get_transaction_synchronization(self):
        return self._transaction_synchronization

    def get_default_timeout(self):
        return self._default_timeout

    def set_default_timeout(self, timeout):
        self._default_timeout = timeout

    def set_nested_transaction_allowed(self, allowed):
        self._nested_transaction_allowed = allowed

    def get_nested_transaction_allowed(self):
        return self._nested_transaction_allowed

    def set_validate_existing_transaction(self, validate):
        self._validated_existing_transaction = validate

    def get_validate_existing_transaction(self):
        return self._validated_existing_transaction

    def set_global_rollback_on_participation_failure(self, rollback):
        self._global_rollback_on_participation_failure = rollback

    def should_commit_on_global_rollback_only(self):
        return False

    def get_global_rollback_on_participation_failure(self):
        return self._global_rollback_on_participation_failure

    def is_fail_early_on_global_rollback_only(self):
        return self._fail_early_on_global_rollback_only

    def set_fail_early_on_global_rollback_only(self, fail_early_on_global_rollback_only):
        self._fail_early_on_global_rollback_only = fail_early_on_global_rollback_only

    def set_rollback_on_commit_failure(self, rollback_on_commit_failure):
        self._rollback_on_commit_failure = rollback_on_commit_failure

    def is_rollback_on_commit_failure(self):
        return self._rollback_on_commit_failure

    def get_transaction(self, definition):
        transaction = self.do_get_transaction()
        if definition is None:
            definition = DefaultTransactionDefinition()
        if self.is_existing_transaction(transaction):
            return self.handle_existing_transaction(definition, transaction)
        if definition.get_timeout() < TransactionDefinition.TIMEOUT_DEFAULT:
            raise Exception
        if definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_MANDATORY:
            raise Exception
        elif definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_REQUIRED or \
                definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW or \
                definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_NESTED:
            suspended_resources = self.suspend(None)
            try:
                new_synchronization = self.get_transaction_synchronization() != self.SYNCHRONIZATION_NEVER
                status = self.new_transaction_status(
                    definition, transaction, True, new_synchronization, suspended_resources
                )
                self.do_begin(transaction, definition)
                self.prepare_synchronization(status, definition)
                return status
            except RuntimeError, ex:
                self.resume(None, suspended_resources)
                raise ex
            except Exception, e:
                self.resume(None, suspended_resources)
                raise e
        else:
            new_synchronization = self.get_transaction_synchronization() == self.SYNCHRONIZATION_ALWAYS
            return self.prepare_transaction_status(definition, None, True, new_synchronization, None)

    def handle_existing_transaction(self, definition, transaction):
        if definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_NEVER:
            raise Exception('Existing transaction found for transaction marked with propagation never')
        if definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_NOT_SUPPORTED:
            suspended_resources = self.suspend(transaction)
            new_synchronization = self.get_transaction_synchronization() != self.SYNCHRONIZATION_ALWAYS
            return self.prepare_transaction_status(definition, None, False, new_synchronization, suspended_resources)

        if definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW:
            suspended_resources = self.suspend(transaction)
            try:
                new_synchronization = self.get_transaction_synchronization() != self.SYNCHRONIZATION_NEVER
                status = self.new_transaction_status(
                    definition, transaction, True, new_synchronization, suspended_resources
                )
                self.do_begin(transaction, definition)
                self.prepare_synchronization(status, definition)
                return status
            except RuntimeError, begin_ex:
                self.resume_after_begin_exception(transaction, suspended_resources, begin_ex)
                raise begin_ex
            except Exception, begin_err:
                self.resume_after_begin_exception(transaction, suspended_resources, begin_err)
                raise begin_err
        if definition.get_propagation_behavior() == TransactionDefinition.PROPAGATION_NESTED:
            raise Exception('No Nested')

        new_synchronization = self.get_transaction_synchronization() != self.SYNCHRONIZATION_NEVER
        self.prepare_transaction_status(definition, transaction, False, new_synchronization, None)

    def prepare_transaction_status(self,
                                   definition,
                                   transaction,
                                   new_transaction,
                                   new_synchronization,
                                   suspended_resources):
        status = self.new_transaction_status(
            definition, transaction, new_transaction, new_synchronization, suspended_resources)
        self.prepare_synchronization(status, definition)
        return status

    def new_transaction_status(self,
                               definition,
                               transaction,
                               new_transaction,
                               new_synchronization,
                               suspended_resources):
        actual_new_synchronization = False
        return DefaultTransactionStatus(
            transaction, new_transaction, actual_new_synchronization,
            definition.is_read_only(), suspended_resources
        )

    def prepare_synchronization(self, status, definition):
        if status.is_new_synchronization():
            pass

    def determine_timeout(self, definition):
        if definition.get_timeout() != TransactionDefinition.TIMEOUT_DEFAULT:
            return definition.get_timeout()
        return self.get_default_timeout()

    def suspend(self, transaction):
        suspended_resource = self.do_suspend(transaction)
        return SuspendedResourcesHolder(suspended_resource)

    def resume(self, transaction, resources_holder):
        suspended_resources = resources_holder.supsended_resources
        if suspended_resources is not None:
            self.do_resume(transaction, suspended_resources)

    def resume_after_begin_exception(self,
                                     transaction,
                                     suspended_resources, begin_ex):
        ex_message = "Inner transaction begin exception overridden by outer transaction resume exception"
        try:
            self.resume(transaction, suspended_resources)
        except RuntimeError, resume_ex:
            raise resume_ex
        except Exception, resume_err:
            raise resume_err

    def doSuspendSynchronization(self):
        pass

    def doResumeSynchronization(self, suspended):
        pass

    def do_resume(self, transaction, suspended):
        raise Exception("Transaction manager [" + self.__class__.__name__ + "] does not support transaction suspension")

    def commit(self, status):
        return
        # if status.is_completed():
        #     raise Exception
        # def_status = status
        # if def_status.is_local_rollback_only():
        #     self.process_rollback(def_status)
        #     return
        # if not self.should_commit_on_global_rollback_only() and def_status.is_global_rollback_only():
        #     self.process_rollback(def_status)
        #     if status.is_new_transaction() or self.is_fail_early_on_global_rollback_only():
        #         raise Exception
        #     return
        # self.process_commit(def_status)

    def process_commit(self, status):
        try:
            before_completion_invoked = False
            try:
                self.prepare_for_commit(status)
                self.trigger_before_commit(status)
                self.trigger_before_completion(status)
                before_completion_invoked = True
                global_rollback_only = False
                if status.is_new_transaction() or self.is_fail_early_on_global_rollback_only():
                    global_rollback_only = status.is_global_rollback_only()
                if status.is_new_transaction():
                    self.do_commit(status)
                if global_rollback_only:
                    raise Exception
            except Exception, ex:
                raise ex
            try:
                self.trigger_after_commit(status)
            finally:
                self.trigger_after_completion(status, 0) #TransactionSynchronization.STATUS_COMMITTED
        finally:
            self.cleanup_after_completion(status)

    def rollback(self, status):
        if status.is_completed():
            raise Exception
        def_status = status
        self.process_rollback(def_status)

    def process_rollback(self, status):
        try:
            try:
                self.trigger_before_completion(status)
                if status.is_new_transaction():
                    self.do_rollback(status)
                elif status.has_transaction():
                    if status.is_local_rollback_only() or self.get_global_rollback_on_participation_failure():
                        self.do_set_rollback_only(status)
                    else:
                        pass
                else:
                    pass
            except RuntimeError, ex:
                self.trigger_after_completion(status, 0)
                raise ex
            except Exception, err:
                self.trigger_after_completion(status, 0)
            self.trigger_after_completion(status, 0)
        finally:
            self.cleanup_after_completion(status)

    def do_rollback_on_commit_exception(self, status, ex):
        try:
            if status.is_new_transaction():
                self.do_rollback(status)
            elif status.has_transaction() and self._global_rollback_on_participation_failure:
                self.do_set_rollback_only(status)
        except RuntimeError, rbex:
            self.trigger_after_completion(status, 0)
            raise rbex
        except Exception, e:
            self.trigger_after_completion(status, 0)
            raise e
        self.trigger_after_completion(status, 0)

    def trigger_before_commit(self, status):
        if status.is_new_synchronization():
            pass

    def trigger_before_completion(self, status):
        if status.is_new_synchronization():
            pass

    def trigger_after_commit(self, status):
        if status.is_new_synchronization():
            pass

    def trigger_after_completion(self, status, completion_status):
        if status.is_new_synchronization():
            pass

    def invoke_after_completion(self, synchronizations, completion_status):
        pass

    def cleanup_after_completion(self, status):
        status.set_completed()
        if status.is_new_transaction():
            self.do_cleanup_after_completion(status.get_transaction())
        if status.get_suspended_resources is not None:
            self.resume(status.get_transaction(), status.get_suspended_resources())

    def do_get_transaction(self):
        pass

    def is_existing_transaction(self, transaction):
        return False

    def useSavepointForNestedTransaction(self):
        return True

    def do_begin(self, transaction, definition):
        pass

    def do_suspend(self, transaction):
        #raise Exception
        return None

    def prepare_for_commit(self, status):
        pass

    def do_commit(self, status):
        pass

    def do_rollback(self, status):
        pass

    def do_set_rollback_only(self, status):
        pass

    def registerAfterCompletionWithExistingTransaction(self, transaction, synchronizations):
        pass

    def do_cleanup_after_completion(self, transaction):
        pass

    def is_existing_transaction(self, transaction):
        return False


class SuspendedResourcesHolder(object):
    def __init__(self,
                 suspended_resources,
                 suspended_synchronizations=None,
                 name=None,
                 read_only=None,
                 isolation_level=None,
                 was_active=None):
        self._suspended_resources = suspended_resources
        self._suspended_synchronizations = suspended_synchronizations
        self._name = name
        self._read_only = read_only
        self._isolation_level = isolation_level
        self._was_active= was_active














