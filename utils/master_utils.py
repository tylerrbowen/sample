__author__ = 'AH0137307'
from operator import attrgetter


class MasterUtils(object):

    @classmethod
    def adjust_version_instants(cls, now, from_time, to_time, documents):
        for doc in documents:
            from_instant = doc.get_version_from_instant()
            if from_instant is None:
                doc.set_version_from_instant(from_time)
        copy = documents[:]
        copy = sorted(copy, key=attrgetter('version_from_instant'))
        latest_document_version_to = copy[-1].version_to_instant()
        prev_document = None
        for doc in copy:
            if latest_document_version_to is None:
                doc.set_version_to_instant(to_time)
                if prev_document is not None:
                    prev_document.set_version_to_instant(doc.get_version_from_instant())
            else:
                doc.set_version_to_instant(latest_document_version_to)
            prev_document = doc
            doc.set_correction_from_instant(now)
            doc.set_correction_to_instant(None)
        return copy

    @classmethod
    def map_to_unique_ids(cls, documents):
        return map(lambda x: x.get_unique_id(), documents)
