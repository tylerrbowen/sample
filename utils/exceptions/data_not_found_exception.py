from portfolio_system_runtime_exception import PortfolioSystemRuntimeException


class DataNotFoundException(PortfolioSystemRuntimeException):

    def __init__(self,
                 message,
                 cause=None):
        super(DataNotFoundException, self).__init__(message, cause)
