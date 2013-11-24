from portfolio_system_runtime_exception import PortfolioSystemRuntimeException


class ConnectionUnavailableException(PortfolioSystemRuntimeException):
    def __init__(self, message):
        super(ConnectionUnavailableException, self).__init__(message)

