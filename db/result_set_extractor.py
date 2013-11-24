"""
ResultSetExtractor
    extract_data
"""

class ResultSetExtractor(object):
    def __init__(self):
        return

    def extract_data(self, result_set, *args, **kwargs):
        raise NotImplementedError()


class RowMapperResultSetExtractor(ResultSetExtractor):

    def __init__(self,
                 row_mapper,
                 rows_expected=None):
        super(RowMapperResultSetExtractor, self).__init__()
        self._row_mapper = row_mapper
        self._rows_expected = rows_expected

    def extract_data(self, result_set, *args, **kwargs):
        results = []
        row_num = 0
        for r in result_set:
            results.append(self._row_mapper.map_row(r, row_num))
            row_num += 1
        return results



