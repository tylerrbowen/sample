
from abc import ABCMeta, abstractmethod


class SqlFragment(object):
    """
    Single fragment in the elsql AST.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_sql(self, buf, bundle, param_source):
        """
        Convert this fragment to SQL, appending it to the specified buffer.
        @param buf  the buffer to append to, not null
        @param bundle  the elsql bundle for context, not null
        @param paramSource  the SQL parameters, not null
        """
        pass

