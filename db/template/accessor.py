

class Accessor(object):
    def __init__(self):
        self._data_source = None
        #self._exception_translator = None
        #self._lazy_init = True

    def set_data_source(self, data_source):
        self._data_source = data_source

    def get_data_source(self):
        return self._data_source


