
from sql_fragment import SqlFragment


class TextSqlFragment(SqlFragment):

    def __init__(self,
                 text):
        text = text.strip()
        if len(text) == 0:
            text = ''
        self._text = text + ' '

    def get_text(self):
        return self._text

    def to_sql(self, buf, bundle, param_source):
        buf += self._text if self._text is not None else ' '

    def __str__(self):
        return self.__class__.__name__ + ':' + self._text


