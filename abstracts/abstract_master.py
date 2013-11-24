__author__ = 'AH0137307'
from source.change_manager_base import ChangeProvider


class AbstractMaster(object):
    def __init__(self):
        pass

    def get(self,
            unique_id=None,
            object_id=None,
            version_correction=None,
            unique_ids=None):
        pass

    def add(self, document):
        pass

    def update(self, document):
        pass

    def remove(self, object_identifiable):
        pass

    def correct(self, document):
        pass

    def replace_version(self,
                        document=None,
                        unique_id=None,
                        replacement_documents=None):
        """
        either:
            document or
            unique_id + replacement_documents
        """
        pass

    def replace_all_versions(self,
                             object_identifiable,
                             replacement_documents):
        pass

    def replace_versions(self,
                         object_identifiable,
                         replacement_documents):
        pass

    def remove_version(self,
                       unique_id):
        pass

    def add_version(self,
                    object_identifiable,
                    document):
        pass


class AbstractChangeProvidingMaster(AbstractMaster, ChangeProvider):
    def __init__(self):
        super(AbstractChangeProvidingMaster, self).__init__()




