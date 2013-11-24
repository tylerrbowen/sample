from utils.new_enum import EnumeratedType, Item


class ExternalIdSearchType(EnumeratedType):
    EXACT = Item('Exact')
    ALL = Item('All')
    ANY = Item('Any')
    NONE = Item('None')

