from default_transaction_defintion import DefaultTransactionDefinition


class TransactionOperations(object):
    def __init__(self, *args, **kwargs):
        pass

    def execute(self, action):
        pass


class TransactionTemplate(DefaultTransactionDefinition, TransactionOperations):

    def __init__(self,
                 transaction_manager=None,
                 transaction_definition=None):
        super(TransactionTemplate, self).__init__(transaction_definition)
        self._transaction_manager = transaction_manager
        self._transaction_definition = transaction_definition

    def set_transaction_manager(self, transaction_manager):
        self._transaction_manager = transaction_manager

    def get_transaction_manager(self):
        return self._transaction_manager

    def after_properties_set(self):
        if self._transaction_manager is None:
            raise Exception('Transaction manager required')

    def execute(self, action):
        status = self._transaction_manager.get_transaction(self)
        try:
            result = action.do_in_transaction(status)
        except RuntimeError, ex:
            self.rollback_on_exception(status, ex)
            raise ex
        except Exception, e:
            self.rollback_on_exception(status, e)
            raise e
        self._transaction_manager.commit(status)
        return result

    def rollback_on_exception(self, status, ex):
        try:
            self._transaction_manager.rollback(status)
        except Exception, e:
            raise e

