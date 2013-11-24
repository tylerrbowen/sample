
from ids.object_identifiable import ObjectIdentifiable
from ids.mutable_unique_identifiable import MutableUniqueIdentifiable
from ids.unique_identifiable import UniqueIdentifiable
from abc import ABCMeta, abstractmethod


class AbstractDocument(UniqueIdentifiable,
                       MutableUniqueIdentifiable,
                       ObjectIdentifiable):
    def __init__(self,
                 object_id=None,
                 unique_id=None):

        self._version_from_instant = None
        self._version_to_instant = None
        self._correction_from_instant = None
        self._correction_to_instant = None

    def get_object_id(self):
        return self.get_unique_id().\
            get_object_id()

    @abstractmethod
    def get_value(self):
        pass
        # return self._unique_id.\
        #     get_value()



    def is_latest(self):
        return self.get_version_to_instant is None and \
               self.get_correction_to_instant() is None

    def __eq__(self, other):
        if not isinstance(other, AbstractDocument):
            return False
        return self.get_version_from_instant() == other.get_version_from_instant() and \
            self.get_version_to_instant() == other.get_version_to_instant() and \
            self.get_correction_from_instant() == other.get_correction_from_instant() and \
            self.get_correction_to_instant() == other.get_correction_to_instant()

    def copy_from(self, copy=None):
        if not copy:
            copy = AbstractDocument()
        copy.set_unique_id(self.get_unique_id())
        copy.set_version_from_instant(self.get_version_from_instant())
        copy.set_version_to_instant(self.get_version_to_instant())
        copy.set_correction_from_instant(self.get_correction_from_instant())
        copy.set_correction_to_instant(self.get_correction_to_instant())
        return copy

    def get_version_from_instant(self):
        return self._version_from_instant

    def get_version_to_instant(self):
        return self._version_to_instant

    def get_correction_from_instant(self):
        return self._correction_from_instant

    def get_correction_to_instant(self):
        return self._correction_to_instant

    def set_version_from_instant(self, version_from_instant):
        self._version_from_instant = version_from_instant

    def set_version_to_instant(self, version_to_instant):
        self._version_to_instant = version_to_instant

    def set_correction_from_instant(self, correction_from_instant):
        self._correction_from_instant = correction_from_instant

    def set_correction_to_instant(self, correction_to_instant):
        self._correction_to_instant = correction_to_instant