

from lazr.enum import EnumeratedType, Item, MetaEnum


class FuncItem(Item):
    def __init__(self,
                 func,
                 title,
                 description=None,
                 url=None):
        super(FuncItem, self).__init__(title,
                                      description,
                                      url)
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class FuncMetaEnum(MetaEnum):
    item_type = FuncItem


class FuncEnum:
    __metaclass__ = FuncMetaEnum



