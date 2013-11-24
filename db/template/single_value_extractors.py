
from db.result_set_extractor import ResultSetExtractor


class SingleValueExtractor(ResultSetExtractor):

    def extract_data(self, result_set, *args, **kwargs):
        try:
            return result_set[0][0]
        except IndexError, AttributeError:
            return None
