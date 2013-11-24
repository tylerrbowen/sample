

from container_sql_fragment import ContainerSqlFragment

class NameSqlFragment(ContainerSqlFragment):

    def __init__(self,
                 name):
        super(NameSqlFragment, self).__init__()
        self._name = name

    def get_name(self):
        return self._name

    def __str__(self):
        return self.__class__.__name__ + ':' + self._name + ' ' + self.get_fragments().__str__()


