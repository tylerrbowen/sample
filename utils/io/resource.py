from abc import ABCMeta, abstractmethod
from utils.io.input_stream_source import InputStreamSource

__author__ = 'Tyler'


class Resource(InputStreamSource):
    """
    Interface for a resource descriptor that abstracts from the actual
    type of underlying resource, such as a file or class path resource.
    <p>An InputStream can be opened for every resource if it exists in
    physical form, but a URL or File handle can just be returned for
    certain resources. The actual behavior is implementation-specific.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def exists(self):
        """
        Return whether this resource actually exists in physical form.
        <p>This method performs a definitive existence check, whereas the
        existence of a {@code Resource} handle only guarantees a
        valid descriptor handle.
        """
        pass

    @abstractmethod
    def is_readable(self):
        """
        Return whether the contents of this resource can be read,
        e.g. via {@link #getInputStream()} or {@link #getFile()}.
        <p>Will be {@code true} for typical resource descriptors;
        note that actual content reading may still fail when attempted.
        However, a value of {@code false} is a definitive indication
        that the resource content cannot be read.
        """
        pass

    @abstractmethod
    def is_open(self):
        pass

    @abstractmethod
    def get_url(self):
        pass

    @abstractmethod
    def get_uri(self):
        pass

    @abstractmethod
    def get_file(self):
        pass

    @abstractmethod
    def content_length(self):
        pass

    @abstractmethod
    def last_modified(self):
        pass

    @abstractmethod
    def create_relative(self, relative_path):
        pass

    @abstractmethod
    def get_filename(self):
        pass

    @abstractmethod
    def get_description(self):
        pass