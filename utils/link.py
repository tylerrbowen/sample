"""
Link
AbstractLink
LinkUtils
"""
from ids.external_id_bundle import ExternalIdBundle
from ids.unique_identifiable import UniqueIdentifiable

__author__ = 'AH0137307'
from __init__ import ObjectIdentifiable


class Link(ObjectIdentifiable):
    """
    external_id IS ExternalIdBundle
    """
    def __init__(self,
                 object_id=None,
                 external_id=None,
                 **kwargs):
        super(Link, self).__init__(object_id)
        self._object_id = object_id
        self._external_id = external_id

    def get_object_id(self):
        return self._object_id

    def get_external_id(self):
        return self._external_id

    def resolve(self, link_resolver):
        pass


class AbstractLink(Link):

    def __init__(self,
                 object_id=None,
                 unique_id=None,
                 external_id=None,
                 external_id_bundle=ExternalIdBundle.EMPTY()):
        if unique_id:
            object_id = unique_id.get_object_id()
        if external_id:
            external_id_bundle = ExternalIdBundle.of(external_id)
        super(AbstractLink, self).__init__(self,
                                           object_id,
                                           external_id_bundle)

    def set_object_id(self, object_id=None):
        self._object_id = object_id

    def set_external_id(self, external_id_bundle):
        self._external_id = external_id_bundle

    def __eq__(self, other):
        if not isinstance(other, AbstractLink):
            return False
        return self.get_object_id() == other.get_object_id() and \
            self.get_external_id() == other.get_external_id()

    def add_external_id(self, external_id):
        self.set_external_id(self.get_external_id().with_external_id(external_id))

    def add_external_ids(self, external_ids):
        self.set_external_id(self.get_external_id().with_external_ids(external_ids))

    def get_best(self):
        return LinkUtils.best(self)

    def get_best_name(self):
        return LinkUtils.best_name(self)

    def resolve(self, link_resolver):
        return link_resolver.resolve(self)

    def __eq__(self, other):
        if not isinstance(other, AbstractLink):
            return False
        return self.get_object_id() == other.get_object_id and \
            self.get_external_id() == other.get_external_id()


class LinkUtils(object):
    def __init__(self):
        pass

    @classmethod
    def best(cls, link):
        object_id = link.get_object_id()
        bundle = link.get_external_id()
        if object_id:
            return object_id
        else:
            return bundle

    @classmethod
    def best_name(cls, link):
        object_id = link.get_object_id()
        bundle = link.get_external_id()
        if bundle is not None and bundle.size() > 0:
            return bundle
        else:
            return object_id.__str__()


class LinkResolver(UniqueIdentifiable):
    def resolve(self, link):
        pass






