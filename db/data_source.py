import pyodbc


class CommonDataSource(object):
    def __init__(self):
        pass

    def get_log_writer(self):
        pass

    def set_log_writer(self, log_writer):
        pass

    def set_login_timeout(self, seconds):
        pass

    def get_login_timeout(self):
        pass

    def get_parent_logger(self):
        pass


class Wrapper(object):
    def __init__(self):
        pass

    def unwrap(self, iface):
        pass

    def is_wrapper_for(self, iface):
        pass


class DataSource(CommonDataSource, Wrapper):
    def __init__(self):
        super(DataSource, self).__init__()

    def get_connection(self,
                       *args,
                       **kwargs):
        pass


