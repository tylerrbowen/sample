

class OperationContext(object):
    def __init__(self, region_repository=None):
        self._session = None
        self._region_repository = region_repository

    def set_region_repository(self, region_repository):
        self._region_repository = region_repository

    def get_region_repository(self):
        return self._region_repository

    def set_session(self, session):
        self._session = session

    def get_session(self):
        return self._session
