from new_enum import EnumeratedType, Item


class CalculationMode(EnumeratedType):
    """
    Enumeration of strict versus lenient calculation.
    LENIENT Lenient calculation.
    STRICT Strict calculation.
    """
    LENIENT = Item('LENIENT')
    STRICT = Item('STRICT')
