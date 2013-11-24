from lazr.enum import EnumeratedType, Item


class ExpiryAccuracy(EnumeratedType):

    MIN_HOUR_DAY_MONTH_YEAR = Item('MIN_HOUR_DAY_MONTH_YEAR')
    HOUR_DAY_MONTH_YEAR = Item('HOUR_DAY_MONTH_YEAR')
    DAY_MONTH_YEAR = Item('DAY_MONTH_YEAR')
    MONTH_YEAR = Item('MONTH_YEAR')
    YEAR = Item('YEAR')
