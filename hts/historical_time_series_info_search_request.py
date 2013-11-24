import numpy as np
from utils.regex_utils import RegexUtils
from abstracts.abstract_search_request import AbstractSearchRequest
from ids.external_id_search import ExternalIdSearch


class HistoricalTimeSeriesInfoSearchRequest(AbstractSearchRequest):

    def __init__(self,
                 external_id=None,
                 external_id_bundle=None):
        super(HistoricalTimeSeriesInfoSearchRequest, self).__init__()
        self._external_id_value = None
        self._external_id_search = None
        self._validity_date = None
        self._name = None
        self._data_source = None
        self._data_provider = None
        self._data_field = None
        self._observation_time = None
        self._object_ids = None
        if external_id_bundle is not None:
            self.add_external_ids(external_id_bundle)
        elif external_id is not None:
            self.add_external_id(external_id)

    def add_object_id(self, info_id):
        if self._object_ids is None:
            self._object_ids = []
        self._object_ids.append(info_id.get_object_id())

    def set_object_ids(self, info_ids):
        if info_ids is None:
            self._object_ids = None
        else:
            self._object_ids = []
            for exchange_id in info_ids:
                self._object_ids.append(exchange_id.get_object_id())

    def add_external_id(self, external_id):
        self.add_external_ids(*(external_id,))

    def add_external_ids(self, *external_ids):
        if self.get_external_id_search() is None:
            self.set_external_id_search(ExternalIdSearch(external_ids=external_ids))
        else:
            self.get_external_id_search().add_external_ids(external_ids)

    def matches(self, document):
        if not isinstance(document, HistoricalTimeSeriesInfoSearchRequest):
            return False
        info = document.get_info()
        if self.get_object_ids() is not None and document.get_object_id() not in self.get_object_ids():
            return False
        if self.get_name() is not None and not RegexUtils.wild_card_match(self.get_name(), info.get_name()):
            return False
        if self.get_data_source() is not None and not self.get_data_source().__eq__(info.get_data_source()):
            return False
        if self.get_data_provider() is not None and not self.get_data_provider().__eq__(info.get_data_provider()):
            return False
        if self.get_data_field() is not None and not self.get_data_field().__eq__(info.get_data_field()):
            return False
        if self.get_observation_time() is not None and not self.get_observation_time().__eq__(info.get_observation_time()):
            return False
        if self.get_external_id_value() is not None:
            doc_bundle = info.get_external_id_bundle().to_bundle()
            success = False
            for identifier in doc_bundle.get_external_ids():
                if RegexUtils.wild_card_match(self.get_external_id_value(), identifier.get_value()):
                    success = True
                    break
            if not success:
                return False
        return True

    def __str__(self):
        s = self.__class__.__name__
        s += '[' + self.get_external_id_search().__str__() + ', '
        s += self.get_external_id_value().__str__() + ', '
        s += self.get_data_source().__str__() + ', '
        s += self.get_data_provider().__str__() + ', '
        s += self.get_data_field().__str__() + ', '
        s += self.get_observation_time().__str__() + ']'
        return s


    def __eq__(self, other):
        if self is other:
            return True
        if not other is None and isinstance(other, HistoricalTimeSeriesInfoSearchRequest):
            return np.all(self.get_object_ids() == other.get_object_ids()) and \
                self.get_external_id_search() == other.get_external_id_search() and \
                self.get_external_id_value() == other.get_external_id_value() and \
                self.get_validity_date() == other.get_validity_date() and \
                self.get_name() == other.get_name() and \
                self.get_data_source() == other.get_data_source() and \
                self.get_data_provider() == other.get_data_provider() and \
                self.get_data_field() == other.get_data_field() and \
                self.get_observation_time() == other.get_observation_time() and \
                super(HistoricalTimeSeriesInfoSearchRequest, self).__eq__(other)
        return False

    def __hash__(self):
        h = 7
        h += h * 31 + self.get_object_ids().__hash__()
        h += h * 31 + self.get_external_id_search().__hash__()
        h += h * 31 + self.get_external_id_value().__hash__()
        h += h * 31 + self.get_validity_date().__hash__()
        h += h * 31 + self.get_name().__hash__()
        h += h * 31 + self.get_data_source().__hash__()
        h += h * 31 + self.get_data_provider().__hash__()
        h += h * 31 + self.get_data_field().__hash__()
        h += h * 31 + self.get_observation_time().__hash__()
        return h ^ super(HistoricalTimeSeriesInfoSearchRequest, self).__hash__()

    def get_object_ids(self):
        return self._object_ids

    def get_external_id_search(self):
        return self._external_id_search

    def set_external_id_search(self, external_id_search):
        self._external_id_search = external_id_search

    def get_external_id_value(self):
        return self._external_id_value

    def set_external_id_value(self, external_id_value):
        self._external_id_value = external_id_value

    def get_validity_date(self):
        return self._validity_date

    def set_validity_date(self, validity_date):
        self._validity_date = validity_date

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_data_source(self):
        return self._data_source

    def set_data_source(self, data_source):
        self._data_source = data_source

    def get_data_provider(self):
        return self._data_provider

    def set_data_provider(self, data_provider):
        self._data_provider = data_provider

    def get_data_field(self):
        return self._data_field

    def set_data_field(self, data_field):
        self._data_field = data_field

    def get_observation_time(self):
        return self._observation_time

    def set_observation_time(self, observation_time):
        self._observation_time = observation_time

