from class_utils import ClassUtils

class ResourceUtils:

    CLASSPATH_URL_PREFIX = "classpath:"
    FILE_URL_PREFIX = "file:"
    URL_PROTOCOL_FILE = "file"
    URL_PROTOCOL_ZIP = "zip"
    URL_PROTOCOL_VFS = "vfs"

    @classmethod
    def is_url(cls, resource_location):
        if resource_location is None:
            return False
        if resource_location.starts_with(cls.CLASSPATH_URL_PREFIX):
            return True
        try:
            #URL(resource_location)
            pass
        except Exception, ex:
            raise Exception(ex)

    @classmethod
    def get_url(cls, resource_location):
        assert resource_location is not None
        if resource_location.starts_with(cls.CLASSPATH_URL_PREFIX):
            path = resource_location[:len(cls.CLASSPATH_URL_PREFIX)]

    @classmethod
    def get_file(cls, resource_location):
        assert resource_location is not None
        if resource_location.starts_with(cls.CLASSPATH_URL_PREFIX):
            path = resource_location[:len(cls.CLASSPATH_URL_PREFIX)]
            abs_path, module_name = path.rsplit('//', 1)
            description = 'class path resource [' + path + ']'
            url = ClassUtils.get_default_class_loader().get_resource(abs_path, module_name)
            if url is None:
                raise IOError('could not find ' + description)
            return url

    @classmethod
    def is_file_url(cls, url):
        protocol = url.get_protocol()
        return cls.URL_PROTOCOL_FILE.__eq__(protocol)
