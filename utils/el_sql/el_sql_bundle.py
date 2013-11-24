import sys
import io
from db.template.map_sql_parameter_source import SqlParameterSource
import pkg_resources
from pkg_resources import DefaultProvider
from el_sql_parser import ElSqlParser


class ElSqlStringBuffer(object):
    def __init__(self):
        self._buf = ''

    def __add__(self, other):
        self._buf += other
        return self

    def __len__(self):
        return len(self._buf)

    def __getitem__(self, item):
        return self._buf.__getitem__(item)
    def __str__(self):
        return self._buf


class ElSqlResource(DefaultProvider):
    def __init__(self, module, file_):
        DefaultProvider.__init__(self, module)
        self._file = file_

    def get_resource_stream(self):
        return DefaultProvider.get_resource_stream(self, None, self._file)

    def get_resource_string(self):
        return DefaultProvider.get_resource_string(self, None, self._file)

    def has_resource(self):
        return DefaultProvider.has_resource(self, self._file)


class ElSqlBundle(object):
    """
    A bundle of elsql formatted SQL.
    The bundle encapsulates the SQL needed for a particular feature.
    This will typically correspond to a data access object, or set of related tables.
    This class is immutable and thread-safe.
    private final Map<String, NameSqlFragment> _map;
    private final ElSqlConfig _config;

    """
    def __init__(self,
                 sql_map,
                 config):
        """
        @param map  the map of names, not null
        @param config  the config to use, not null
        """
        if sql_map is None:
            raise TypeError('Fragment map must not be null')
        if config is None:
            raise TypeError('Config must not be null')
        self._map = sql_map
        self._config = config

    @classmethod
    def of(cls, config, clazz_type, module_):
        """
        Loads external SQL based for the specified type.
        The type is used to identify the location and name of the ".elsql" file.
        The loader will attempt to find and use two files, using the full name of
        the type to query the class path for resources.
        The first resource searched for is optional - the file will have the suffix
        "-ConfigName.elsql", such as "com/foo/Bar-MySql.elsql".
        The second resource searched for is mandatory - the file will just have the
        ".elsql" suffix, such as "com/foo/Bar.elsql".
        The config is designed to handle some, but not all, database differences.
        Other differences should be handled by creating and using a database specific
        override file (the first optional resource is the override file).
        @param config  the config, not null
        @param type  the type, not null
        @return the bundle, not null
        @throws TypeError if the input cannot be parsed
        """
        if config is None:
            raise TypeError('Config must not be null')
        if module_ is None:
            raise TypeError('Type must not be null')
        base_resource = ElSqlResource(module_, clazz_type.__name__ + '.elsql')
        config_resource = ElSqlResource(module_, clazz_type.__name__ + '-' + '.elsql')
        return cls.parse(config, base_resource, config_resource)

    @classmethod
    def parse(cls, config, *resources):
        """
        Parses a bundle from a resource locating a file, specify the config.
        This parses a list of resources. Named blocks in later resources override
        blocks with the same name in earlier resources.
        The config is designed to handle some, but not all, database differences.
        Other differences are handled via the override resources passed in.
        @param config  the config to use, not null
        @param resources  the resources to load, not null
        @return the external identifier, not null
        @throws IllegalArgumentException if the input cannot be parsed
        """
        if config is None:
            raise TypeError('Config must not be null')
        if resources is None:
            raise TypeError('Resources must not be null')
        return cls.parse_resource(resources, config)

    @classmethod
    def parse_resource(cls, resources, config):
        files = []
        for resource in resources:
            lines = cls.load_resource(resource)
            files.append(lines)
        return cls.parse_files(files, config)

    @classmethod
    def parse_files(cls, files, config):
        parsed = dict()
        for lines in files:
            if lines is not None:
                parser = ElSqlParser(lines)
                for p_n, p_v in parser.parse().iteritems():
                    parsed[p_n] = p_v
        return ElSqlBundle(parsed, config)


    @classmethod
    def load_resource(cls, resource):
        in_ = None
        try:
            lst = []
            if resource.has_resource():
                reader = resource.get_resource_stream()
                for line in reader:
                    lst.append(line)
                return lst
        except IOError, ex:
            raise RuntimeError(ex)

    def get_config(self):
        return self._config

    def with_config(self, config):
        """
        Returns a copy of this bundle with a different configuration.
        This does not reload the underlying resources.
        @param config  the new config, not null
        @return a bundle with the config updated, not null
        """
        return ElSqlBundle(self._map, config)

    def get_sql(self, name, param_source=None):
        """
        Finds SQL for a named fragment key, without specifying parameters.
        This finds, processes and returns a named block from the bundle.
        Note that if the SQL contains tags that depend on variables, like AND or LIKE,
        then an error will be thrown.
        @param name  the name, not null
        @return the SQL, not null
        @throws IllegalArgumentException if there is no fragment with the specified name
        @throws RuntimeException if a problem occurs
        """
        if param_source is None:
            param_source = EmptySource()
        fragment = self.get_fragment(name)
        buf = ElSqlStringBuffer()
        fragment.to_sql(buf, self, param_source)
        return buf._buf

    def get_fragment(self, name):
        """
        Gets a fragment by name.
        @param name  the name, not null
        @return the fragment, not null
        @throws IllegalArgumentException if there is no fragment with the specified name
        """
        fragment = self._map.get(name)
        if fragment is None:
            raise TypeError('Unknown Fragment name' + name.__str__())
        return fragment


class EmptySource(SqlParameterSource):
    """
    An empty parameter source.
    """
    def has_value(self, param_name):
        return False

    def get_sql_type(self, param_name):
        return self.TYPE_UNKNOWN

    def get_type_name(self, param_name):
        raise TypeError()

    def get_value(self, param_name):
        return None


def main():
    from db.security.db_security_master import DbSecurityMaster
    import db.security.db_security_master as db_security_master
    from el_sql_config import ElSqlConfig
    d = ElSqlResource(db_security_master, DbSecurityMaster.__name__ + '.elsql')
    d.get_resource_stream()
    #print d.get_resource_string()
    eb = ElSqlBundle.of(ElSqlConfig.SQL_SERVER_2008(), DbSecurityMaster, db_security_master)





