
from transaction_definition import TransactionDefinition


class DefaultTransactionDefinition(TransactionDefinition):
    PREFIX_PROPAGATION = "PROPAGATION_"
    PREFIX_ISOLATION = "ISOLATION_"
    PREFIX_TIMEOUT = "timeout_"
    READ_ONLY_MARKER = "readOnly"

    def __init__(self, other=None, propagation_behavior=None):
        """
        other: TransactionDefinition
        """
        super(DefaultTransactionDefinition, self).__init__()
        if other is not None:
            assert isinstance(other, DefaultTransactionDefinition)
            self._propagation_behavior = other.get_propagation_behavior()
            self._isolation_level = other.get_isolation_level()
            self._timeout = other.get_timeout()
            self._read_only = other.is_read_only()
            self._name = other.get_name()
        else:
            if propagation_behavior is not None:
                self._propagation_behavior = propagation_behavior
            else:
                self._propagation_behavior = self.PROPAGATION_REQUIRED
            self._isolation_level = self.ISOLATION_DEFAULT
            self._timeout = self.TIMEOUT_DEFAULT
            self._read_only = False
            self._name = ''

    def set_propagation_behavior_name(self, constant_name):
        if constant_name not in self.__dict__ or not self.PREFIX_PROPAGATION in constant_name:
            raise Exception('Only values of propagation constants allowed')
        int_constant = self.__dict__[constant_name]
        self.set_propagation_behavior(int_constant)

    def set_propagation_behavior(self, int_constant):
        self._propagation_behavior = int_constant

    def get_propagation_behavior(self):
        return self._propagation_behavior

    def set_isolation_level_name(self, constant_name):
        if constant_name not in self.__dict__ or not self.PREFIX_ISOLATION in constant_name:
            raise Exception('Only values of propagation constants allowed')
        int_constant = self.__dict__[constant_name]
        self.set_isolation_level(int_constant)

    def set_isolation_level(self, int_constant):
        self._isolation_level = int_constant

    def get_isolation_level(self):
        return self._isolation_level

    def set_timeout(self, timeout):
        if timeout < self.TIMEOUT_DEFAULT:
            raise Exception('Timeout must be positive or default')
        self._timeout = timeout

    def get_timeout(self):
        return self._timeout

    def set_read_only(self, read_only):
        self._read_only = read_only

    def is_read_only(self):
        return self._read_only

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def __eq__(self, other):
        return isinstance(other, TransactionDefinition) and self.__str__() == other.__str__()

    def __hash__(self):
        return self.__str__().__hash__()

    def __str__(self):
        return self.get_definition_description().__str__()

    def get_definition_description(self):
        result = ''
        prop = self._propagation_behavior
        for key, value in self.__dict__.iteritems():
            if value == prop and self.PREFIX_PROPAGATION in key:
                result += key
        result += ','
        for key, value in self.__dict__.iteritems():
            if value == prop and self.PREFIX_ISOLATION in key:
                result += key
        result += ','
        if self._timeout != self.TIMEOUT_DEFAULT:
            result += ','
            result += self.PREFIX_TIMEOUT + self._timeout.__str__()
        if self.is_read_only():
            result += ','
            result += self.READ_ONLY_MARKER
        return result



