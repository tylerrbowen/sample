from abstract_file_resolving_resource import AbstractFileResolvingResource
from class_utils import ClassLoader
import os


class ClassPathResource(AbstractFileResolvingResource):

    def __init__(self,
                 file_path,
                 class_loader=None,
                 clazz=None):
        self._file_path = file_path
        self._class_loader = class_loader
        self._clazz = clazz

    def get_path(self):
        return self._file_path

    def get_class_loader(self):
        if self._class_loader is None:
            self._class_loader = ClassLoader()
        return self._class_loader

    def exists(self):
        url = self.get_class_loader().get_resource(self._file_path)
        return url is not None

    def get_input_stream(self):
        if self._clazz is not None:
            is_  = self._clazz.get_resource_as_stream(self._file_path)
        else:
            is_ = self.get_class_loader().get_resource_as_stream(self._file_path)
        if is_ is None:
            raise IOError('cannot find')
        return is_

    def get_url(self):
        if self._clazz is not None:
            is_  = self._clazz.get_resource(self._file_path)
        else:
            is_ = self.get_class_loader().get_resource(self._file_path)
        if is_ is None:
            raise IOError('cannot find')
        return is_

    def create_relative(self, relative_path):
        path_to_use = os.path.join(self._file_path, relative_path)


    def get_description(self):
        s = 'class path resource ['
        path_to_use = self._file_path
        if self._clazz is not None and not path_to_use.starts_with('/'):
            s += self._clazz.__str__()
            s += '/'
        if path_to_use.starts_with('/'):
            path_to_use = path_to_use[1:]
        s += path_to_use
        s += ']'
        return s

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, ClassPathResource):
            return self._file_path.__eq__(other._file_path)

    def __hash__(self):
        return self._file_path.__hash__()
