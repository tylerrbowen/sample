

class ClassLoader:

    def __init__(self):
        return

    def get_resource(self, module_name, class_name):
        module = __import__(module_name)
        clazz = getattr(module, class_name)
        return clazz

class ClassUtils:

    ARRAY_SUFFIX = "[]"
    INTERNAL_ARRAY_PREFIX = "["
    NON_PRIMITIVE_ARRAY_PREFIX = "[L"
    PACKAGE_SEPARATOR = '.'
    INNER_CLASS_SEPARATOR = '$'
    CGLIB_CLASS_SEPARATOR = "$$"
    CLASS_FILE_SUFFIX = ".py"

    primitive_wrapper_type_map = dict()
    primitive_type_to_wrapper_map = dict()
    primitive_type_name_map = dict()
    common_class_cache = dict()

    @classmethod
    def register_common_classes(cls, **classes):
        for clazz in classes:
            cls.common_class_cache[clazz.__name__] = clazz

    @classmethod
    def get_default_class_loader(cls):
        return ClassLoader()
