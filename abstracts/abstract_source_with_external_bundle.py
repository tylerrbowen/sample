__author__ = 'AH0137307'
from source.source_base import SourceWithExternalBundle
from ids.version_correction import VersionCorrection


class AbstractSourceWithExternalBundle(SourceWithExternalBundle):
    def __init__(self):
        super(AbstractSourceWithExternalBundle, self).__init__()

    @classmethod
    def get(cls,
            unique_id=None,
            object_id=None,
            unique_ids=None,
            object_ids=None,
            bundle=None,
            version_correction=None,
            source=None):
        if source is None:
            cls.get(bundle, cls)
        return source.get(bundle=bundle,
                          version_correction=VersionCorrection.LATEST())

    @classmethod
    def get_all(cls,
                bundles,
                source=None,
                version_correction=None):
        """

        :param bundles:
        :param source:
        :param version_correction:
        :return:
        """
        if len(bundles) == 0:
            bundles = dict()
        elif len(bundles) == 1:
            bundle = bundles.iterator().next()
            result = source.get(bundle=bundle,
                                version_correction=version_correction)
            if result is not None and len(result) > 0:
                return {bundle: result}
            else:
                return dict()
        return cls.get_all_single_thread(bundles=bundles,
                                         source=source,
                                         version_correction=version_correction)

    @classmethod
    def get_all_single_thread(cls,
                              bundles=None,
                              source=None,
                              version_correction=None):
        """

        :param bundles: ExternalIdBundle
        :param source: List<ExternalIdBundle>
        :param version_correction: VersionCorrection
        :return:
        """
        results = dict()
        for bundle in bundles:
            result = source.get(bundle=bundle,
                                version_correction=version_correction)
            if result is not None and len(result) > 0:
                results[bundle] = result
        return results

    @classmethod
    def get_single(cls,
                   bundle=None,
                   bundles=None,
                   source=None,
                   version_correction=None):
        """

        :param bundle: ExternalIdBundle
        :param bundles: List<ExternalIdBundle>
        :param source: AbstractSourceWithExternalBundle
        :param version_correction: VersionCorrection
        :return:
        """
        if not source:
            source = cls
        if not version_correction:
            version_correction = VersionCorrection.LATEST()
        if bundle:
            results = source.get(bundle=bundle,
                                 version_correction=version_correction)
            if results is None or len(results) > 0:
                return None
            return results.iterator().next()
        elif bundles:
            if len(bundles) == 0:
                return dict()
            elif len(bundles) == 1:
                bundle = bundles.iterator().next()
                obj = source.get_single(bundle=bundle,
                                        version_correction=version_correction)
                if obj is not None:
                    return {bundle: obj}
                else:
                    return dict()
            else:
                results = dict()
                for bundle in bundles:
                    result = source.get_single(bundle=bundle,
                                               version_correction=version_correction)
                    if result is not None:
                        results[bundle] = result
                return results


class AbstractSecuritySource(AbstractSourceWithExternalBundle):
    def __init__(self):
        super(AbstractSecuritySource, self).__init__()
