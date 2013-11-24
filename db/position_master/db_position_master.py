from db.result_set_extractor import ResultSetExtractor



class PositionDocumentExtractor(ResultSetExtractor):
    def __init__(self):
        super(PositionDocumentExtractor, self).__init__()
        self._last_doc_id = -1
        self._position = None
        self._documents = []

    def extract_data(self, result_set, *args, **kwargs):
        for rs in result_set.__iter__():
            doc_id = rs.position_id
            if self._last_doc_id != doc_id:
                self._last_doc_id = doc_id
                self.build_position(rs, doc_id)
        return self._documents

    def build_position(self, result_row, doc_id):
        pass
        # doc_oid = doc_id
        # version = None
        # index = result_row.index
        # security_id = result_row.security_id
        # dollars = result_row.dollars
        # self._position = TradeModelPosition.of(index=index,
        #                                        security_id=security_id,
        #                                        position_id=doc_oid,
        #                                        dollars=dollars)
        # doc = PositionDocument(self._position)
        # doc.set_plan_id(result_row.plan_id)
        # self._documents.append(doc)


class DbPositionMaster(AbstractDocumentDbMaster):
    IDENTIFIER_SCHEME_DEFAULT = "DbPos";

    def __init__(self,
                 db_connector):
        super(DbPositionMaster, self).__init__(db_connector,
                                               self.IDENTIFIER_SCHEME_DEFAULT)
        self.set_sql_bundle(PositionSqlBundle())

    def get(self, object_id):
        try:
            object_id_value = object_id.get_value()
        except AttributeError:
            if not isinstance(object_id, basestring):
                raise TypeError('Must either be ObjectId or String Id Value')
            object_id_value = object_id
        doc = self.do_get_by_id(object_id_value, PositionDocumentExtractor())
        return doc

    def get_all(self):
        docs = self.do_get_all(PositionDocumentExtractor())
        mapped_results = dict()
        for doc in docs:
            mapped_results[doc.get_id()] = doc
        return mapped_results

    def search(self, request):
        result = PositionSearchResult()
        object_ids = request.get_object_ids()
        args = dict()
        like_args = dict()
        if len(object_ids) > 0:
            buf = ''
            for object_id in object_ids:
               buf +=  '\'' + object_id.get_value().__str__() + '\''
               buf += ', '
            buf = buf[:-2]
            args['sql_search_object_ids'] = buf
        security_id = request.get_security_id_search()
        if security_id is not None:
            args['main.asset_reference_id'] = '\'' + security_id.__str__() + '\''
        plan_id = request.get_plan_id_search()
        if plan_id is not None:
            args['main.idstrategy'] = '\'' + plan_id.__str__() + '\''
        electra_id = request.get_electra_id_search()
        if electra_id is not None:
            like_args['sec.electra_Id'] = '\'%' + electra_id.__str__() + '%\''
        sql = self.get_sql_bundle().search(args, like_args)
        result.set_documents(self.do_search(sql, PositionDocumentExtractor()))
        return result