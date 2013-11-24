

class PortfolioSystemRuntimeException(RuntimeError):
    def __init__(self,
                 message,
                 cause=None):
        super(PortfolioSystemRuntimeException, self).__init__(message, cause)


