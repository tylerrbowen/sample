

from sql_fragment import SqlFragment


class ContainerSqlFragment(SqlFragment):

    def __init__(self):
        self._fragments = []

    def add_fragment(self, child_fragment):
        self._fragments.append(child_fragment)

    def get_fragments(self):
        return self._fragments

    def to_sql(self, buf, bundle, param_source):
        for fragment in self._fragments:
            fragment.to_sql(buf, bundle, param_source)

    def __str__(self):
        return self._fragments.__str__()

