from resource import Resource


class AbstractResource(Resource):
    """
    Convenience base class for {@link Resource} implementations,
    pre-implementing typical behavior.
    <p>The "exists" method will check whether a File or InputStream can
    be opened; "isOpen" will always return false; "getURL" and "getFile"
    throw an exception; and "toString" will return the description.
    """

    def exists(self):
        try:
            return self.get_file().exists()
        except IOError, ex:
            try:
                is_ = self.get_input_stream()
                is_.close()
                return True
            except Exception, isEx:
                return False

    def is_readable(self):
        """
        This implementation always returns {@code true}.
        """
        return True

    def is_open(self):
        return False

    def get_url(self):
        raise IOError(self.get_description() + ' cannot be resolved to URL')

    def get_uri(self):
        raise NotImplementedError()

    def get_file(self):
        raise IOError(self.get_description() + 'cannot be resolved to absolute file path')

    def content_length(self):
        is_ = self.get_input_stream()
        assert is_ is not None
        try:
            size = 0
            buf = int(255)
            read = 0
            for read in is_.read(buf):
                size += read
            return size
        except IOError, e:
            raise IOError(e)
        finally:
            try:
                is_.close()
            except IOError, ex:
                pass

    def last_modified(self):
        last_modified = self.get_file_for_last_modified_check().last_modified()
        if last_modified == 0L:
            raise IOError(self.get_description() + ' cannot be resolved in the file system for last mod date')
        return last_modified

    def get_file_for_last_modified_check(self):
        try:
            self.get_file()
        except IOError, ex:
            raise IOError(ex)

    def create_relative(self, relative_path):
        raise IOError('Cannot create relative resource for ' + self.get_description())

    def get_filename(self):
        return None

    def __str__(self):
        return self.get_description()

    def __eq__(self, other):
        return other is self or \
               (isinstance(other, Resource) and other.get_description().__eq__(self.get_description()))

    def __hash__(self):
        return self.get_description().__hash__()
