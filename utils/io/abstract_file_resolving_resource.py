from abstract_resource import AbstractResource
from resource_utils import ResourceUtils


class AbstractFileResolvingResource(AbstractResource):

    def get_file(self):
        url = self.get_url()
        return ResourceUtils.get_file(url)

    def get_file_for_last_modified_check(self):
        url = self.get_url()
        return self.get_file()

    def exists(self):
        try:
            url = self.get_url()
            if ResourceUtils.is_file_url(url):
                return self.get_file().exists()
            else:
                pass
        except IOError, ex:
            return False

    def is_readable(self):
        try:
            url = self.get_url()
            if ResourceUtils.is_file_url(url):
                file_ = self.get_file()
                return file_.can_read() and not file_.is_directory()
            else:
                return True
        except IOError, ex:
            return False

    def content_length(self):
        url = self.get_url()
        if ResourceUtils.is_file_url(url):
            return self.get_file().length()
        else:
            raise NotImplementedError()

    def last_modified(self):
        url = self.get_url()
        if ResourceUtils.is_file_url(url):
            return super(AbstractFileResolvingResource, self).last_modified()
        else:
            raise NotImplementedError()





