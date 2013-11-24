__author__ = 'AH0137307'
from abstract_source import AbstractSource
from source.change_mvc import ObjectChangeListenerManager, ChangeListener


class AbstractMasterSource(AbstractSource, ObjectChangeListenerManager):
    """
        _master
        _version_correction
        _registered_listeners

        get_master
        get_version_correction
        set_version_correction
        get_document
        get
        get_first_object
        add_change_listener
        remove_change_listener
        change_manager
    """
    def __init__(self,
                 master,
                 version_correction=None):
        self._master = master
        self._version_correction = version_correction
        self._registered_listeners = dict()

    def get_master(self):
        return self._master

    def get_version_correction(self):
        return self._version_correction

    def set_version_correction(self, version_correction):
        self._version_correction = version_correction

    def get_document(self,
                     unique_id=None,
                     object_id=None,
                     version_correction=None):
        if unique_id:
            vc = self.get_version_correction()
            if vc is not None:
                return self.get_master().get(object_id=unique_id.get_object_id(), version_correction=vc)
            else:
                return self.get_master().get(unique_id=unique_id)
        else:
            vc = self.get_version_correction()
            if vc is not None:
                return self.get_master().get(object_id=object_id, version_correction=vc)
            else:
                return self.get_master().get(object_id=object_id, version_correction)

    def get(self,
            source=None,
            unique_id=None,
            object_id=None,
            unique_ids=None,
            object_ids=None,
            version_correction=None):
        if unique_id:
            return self.get_document(unique_id=unique_id)
        elif object_id:
            return self.get_document(object_id=object_id, version_correction=version_correction)

    def get_first_object(self, objects):
        if len(objects) == 0:
            return None
        else:
            return object.__iter__().next()

    def add_change_listener(self,
                            object_id,
                            listener):
        class ChangeListenerInner(ChangeListener):
            def entity_changed(self, event):
                changed_oid = event.get_object_id()
                if changed_oid == object_id:
                    self.listener.object_changed(object_id)
        change_listener = ChangeListenerInner()
        self._registered_listeners[(object_id, listener)] = change_listener
        self.change_manager().add_change_listener(change_listener)

    def remove_change_listener(self,
                               object_id,
                               listener):
        change_listener = self._registered_listeners.pop((object_id, listener))
        self.change_manager().remove_change_listener(change_listener)

    def change_manager(self):
        return self.get_master().get_change_manager()

    def __str__(self):
        st = self.__repr__() + '[' + self.get_master().__str__()
        return st