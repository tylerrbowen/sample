class Attributable(object):
    def __init__(self):
        self._attributes = dict()

    def get_attributes(self):
        return self._attributes

    def set_attributes(self, attributes):
        assert isinstance(attributes, dict)
        self._attributes = attributes

    def add_attribute(self, key, value):
        self._attributes[key] = value