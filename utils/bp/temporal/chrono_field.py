from utils.bp.duration import ChronoUnit
from utils.bp.temporal.temporal_field import TemporalField
from utils.bp.temporal.value_range import ValueRange

from _deps import Item, MetaEnum


class ChronoFieldItem(Item, TemporalField):
    def __init__(self,
                 title,
                 base_unit,
                 range_unit,
                 range_):
        super(ChronoFieldItem, self).__init__(title)
        self.base_unit = base_unit
        self.range_unit = range_unit
        self.range = range_

    def get_name(self):
        return self.title

    def get_base_unit(self):
        return self.base_unit

    def get_range_unit(self):
        return self.range_unit

    def range(self):
        return  self.range

    def is_date_field(self):
        return self.sortkey >= ChronoField.DAY_OF_WEEK.sortkey

    def is_time_field(self):
        print self.sortkey
        print ChronoField.DAY_OF_WEEK.sortkey
        return self.sortkey < ChronoField.DAY_OF_WEEK.sortkey

    def compare(self, t1, t2):
        return t1.get_long(self).__cmp__(t2.get_long(self))

    def check_valid_value(self, value):
        return self.range.check_valid_value(value, self)

    def check_valid_int_value(self, value):
        return self.range.check_valid_int_value(value, self)

    def is_supported_by(self, temporal):
        return temporal.is_supported(self)

    def range_refined_by(self, temporal):
        return temporal.range(self)

    def get_from(self, temporal):
        return temporal.get_long(self)

    def adjust_into(self, temporal, new_value):
        return temporal.with_field(self, new_value)

    def resolve(self, temporal, value):
        return None

    def __str__(self):
        return self.name


class ChronoFieldEnum(MetaEnum):
    item_type = ChronoFieldItem


class ChronoField:

    __metaclass__ = ChronoFieldEnum

    # def __init__(self,
    #              name,
    #              base_unit,
    #              range_unit,
    #              range_):
    #     self.name = name
    #     self.base_unit = base_unit
    #     self.range_unit = range_unit
    #     self.range = range_


    MIN_VALUE = -999999999
    MAX_VALUE = 999999999

    NANO_OF_SECOND = ChronoFieldItem('NanoOfSecond',
                                     ChronoUnit.NANOS,
                                     ChronoUnit.SECONDS,
                                     ValueRange.of(0, 999999999))

    NANO_OF_DAY = ChronoFieldItem('NanoOfDay',
                                  ChronoUnit.NANOS,
                                  ChronoUnit.DAYS,
                                  ValueRange.of(0, 86400L * 1000000000L - 1))

    MICRO_OF_SECOND = ChronoFieldItem('MicroOfSecond',
                                      ChronoUnit.MICROS,
                                      ChronoUnit.SECONDS,
                                      ValueRange.of(0, 999))

    MICRO_OF_DAY =  ChronoFieldItem('MicroOfDay',
                                    ChronoUnit.MICROS,
                                    ChronoUnit.DAYS,
                                    ValueRange.of(0, 86400L * 1000000L - 1)
                           )

    MILLI_OF_SECOND = ChronoFieldItem('MilliOfSecond',
                                      ChronoUnit.NANOS,
                                      ChronoUnit.SECONDS,
                                      ValueRange.of(0, 999))

    MILLI_OF_DAY = ChronoFieldItem('MilliOfDay',
                                   ChronoUnit.NANOS,
                                   ChronoUnit.DAYS,
                                   ValueRange.of(0, 86400L * 1000L - 1))

    SECOND_OF_MINUTE = ChronoFieldItem('SeconOfMinute',
                                       ChronoUnit.MICROS,
                                       ChronoUnit.DAYS,
                                       ValueRange.of(0, 59))

    SECOND_OF_DAY = ChronoFieldItem('SecondOfDay',
                                    ChronoUnit.NANOS,
                                    ChronoUnit.SECONDS,
                                    ValueRange.of(0, 86400L - 1))

    MINUTE_OF_HOUR = ChronoFieldItem('NanoOfDay',
                                     ChronoUnit.NANOS,
                                     ChronoUnit.DAYS,
                                     ValueRange.of(0, 59))

    MINUTE_OF_DAY = ChronoFieldItem('MicroOfSecond',
                                    ChronoUnit.MICROS,
                                    ChronoUnit.SECONDS,
                                    ValueRange.of(0, (24 * 60) - 1))

    HOUR_OF_AMPM = ChronoFieldItem('HourOfAMPM',
                                   ChronoUnit.HOURS,
                                   ChronoUnit.HALF_DAYS,
                                   ValueRange.of(0, 11))

    HOUR_OF_DAY = ChronoFieldItem('HourOfDay',
                                  ChronoUnit.HOURS,
                                  ChronoUnit.DAYS,
                                  ValueRange.of(0, 23))

    CLOCK_HOUR_OF_DAY = ChronoFieldItem('ClockHourOfDay',
                                        ChronoUnit.HALF_DAYS,
                                        ChronoUnit.DAYS,
                                        ValueRange.of(1, 24))

    AMPM_OF_DAY = ChronoFieldItem('AmPmOfDay',
                                  ChronoUnit.NANOS,
                                  ChronoUnit.SECONDS,
                                  ValueRange.of(0, 1))

    DAY_OF_WEEK = ChronoFieldItem('DayOfWeek',
                                  ChronoUnit.DAYS,
                                  ChronoUnit.WEEKS,
                                  ValueRange.of(1, 7))

    ALIGNED_DAY_OF_WEEK_IN_MONTH = ChronoFieldItem('AlignedDayOfWeekInMonth',
                                                   ChronoUnit.DAYS,
                                                   ChronoUnit.MONTHS,
                                                   ValueRange.of(1, 7))

    ALIGNED_DAY_OF_WEEK_IN_YEAR = ChronoFieldItem('AlignedDayOfWeekInYear',
                                                  ChronoUnit.DAYS,
                                                  ChronoUnit.WEEKS,
                                                  ValueRange.of(1, 7))

    DAY_OF_MONTH = ChronoFieldItem('DayOfMonth',
                                   ChronoUnit.DAYS,
                                   ChronoUnit.MONTHS,
                                   ValueRange.of(1, 28, 31))

    DAY_OF_YEAR = ChronoFieldItem('DayOfYear',
                                  ChronoUnit.DAYS,
                                  ChronoUnit.YEARS,
                                  ValueRange.of(1, 365, 366))

    EPOCH_DAY = ChronoFieldItem('EpochDay',
                                ChronoUnit.MICROS,
                                ChronoUnit.SECONDS,
                                ValueRange.of((long) (MIN_VALUE * 365.25), (long) (MAX_VALUE * 365.25)))

    ALIGNED_WEEK_OF_MONTH = ChronoFieldItem('AlignedWeekOfMonth',
                                            ChronoUnit.WEEKS,
                                            ChronoUnit.MONTHS,
                                            ValueRange.of(1, 4, 5))

    ALIGNED_WEEK_OF_YEAR = ChronoFieldItem('AlignedWeekOfYear',
                                           ChronoUnit.WEEKS,
                                           ChronoUnit.YEARS,
                                           ValueRange.of(1, 53))

    MONTH_OF_YEAR = ChronoFieldItem('MonthOfYear',
                                    ChronoUnit.MONTHS,
                                    ChronoUnit.YEARS,
                                    ValueRange.of(1, 12))

    EPOCH_MONTH = ChronoFieldItem("EpochMonth",
                                  ChronoUnit.MONTHS,
                                  ChronoUnit.FOREVER,
                                  ValueRange.of((MIN_VALUE - 1970L) * 12,
                                                (MAX_VALUE - 1970L) * 12L - 1L))

    YEAR_OF_ERA = ChronoFieldItem("YearOfEra",
                                  ChronoUnit.YEARS,
                                  ChronoUnit.FOREVER,
                                  ValueRange.of(1, MAX_VALUE, MAX_VALUE + 1))

    YEAR = ChronoFieldItem('Year',
                           ChronoUnit.YEARS,
                           ChronoUnit.FOREVER,
                           ValueRange.of(MIN_VALUE, MAX_VALUE)
                           )

    ERA = ChronoFieldItem("Era", ChronoUnit.ERAS, ChronoUnit.FOREVER, ValueRange.of(0, 1))

    INSTANT_SECONDS = ChronoFieldItem('InstantSeconds',
                                      ChronoUnit.SECONDS,
                                      ChronoUnit.FOREVER,
                                      ValueRange.of(0x8000000000000000L, 0x7fffffffffffffffL)
                           )

    OFFSET_SECONDS = ChronoFieldItem('OffsetSeconds',
                                     ChronoUnit.SECONDS,
                                     ChronoUnit.FOREVER,
                                     ValueRange.of(-18 * 3600, 18 * 3600)
                           )
    #
    #
    # @classmethod
    # def NANO_OF_SECOND(cls):
    #     return ChronoField('NanoOfSecond',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, 999999999)
    #                        )
    #
    # @classmethod
    # def NANO_OF_DAY(cls):
    #     return ChronoField('NanoOfDay',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.DAYS(),
    #                        ValueRange.of(0, 86400L * 1000000000L - 1)
    #                        )

    # @classmethod
    # def MICRO_OF_SECOND(cls):
    #     return ChronoField('MicroOfSecond',
    #                        ChronoUnit.MICROS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, 999))
    # @classmethod
    # def MICRO_OF_DAY(cls):
    #     return ChronoField('MicroOfDay',
    #                        ChronoUnit.MICROS(),
    #                        ChronoUnit.DAYS(),
    #                        ValueRange.of(0, 86400L * 1000000L - 1)
    #                        )




    # @classmethod
    # def MILLI_OF_SECOND(cls):
    #     return ChronoField('MilliOfSecond',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, 999))



    # @classmethod
    # def SECOND_OF_MINUTE(cls):
    #     return ChronoField('SeconOfMinute',
    #                        ChronoUnit.MICROS(),
    #                        ChronoUnit.DAYS(),
    #                        ValueRange.of(0, 59))



    # @classmethod
    # def SECOND_OF_DAY(cls):
    #     return ChronoField('SecondOfDay',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, 86400L - 1))



    # @classmethod
    # def MINUTE_OF_HOUR(cls):
    #     return ChronoField('NanoOfDay',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.DAYS(),
    #                        ValueRange.of(0, 59))



    # @classmethod
    # def MINUTE_OF_DAY(cls):
    #     return ChronoField('MicroOfSecond',
    #                        ChronoUnit.MICROS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, (24 * 60) - 1))


    # @classmethod
    # def HOUR_OF_AMPM(cls):
    #     return ChronoField('HourOfAMPM',
    #                        ChronoUnit.HOURS(),
    #                        ChronoUnit.HALF_DAYS(),
    #                        ValueRange.of(0, 11))


    # @classmethod
    # def HOUR_OF_DAY(cls):
    #     return ChronoField('HourOfDay',
    #                        ChronoUnit.HOURS(),
    #                        ChronoUnit.DAYS(),
    #                         ValueRange.of(0, 23)),



    # @classmethod
    # def CLOCK_HOUR_OF_DAY(cls):
    #     return ChronoField('ClockHourOfDay',
    #                        ChronoUnit.HALF_DAYS(),
    #                        ChronoUnit.DAYS(),
    #                        ValueRange.of(1, 24))


    # @classmethod
    # def AMPM_OF_DAY(cls):
    #     return ChronoField('AmPmOfDay',
    #                        ChronoUnit.NANOS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of(0, 1))


    # @classmethod
    # def DAY_OF_WEEK(cls):
    #     return ChronoField('DayOfWeek',
    #                        ChronoUnit.DAYS(),
    #                        ChronoUnit.WEEKS(),
    #                        ValueRange.of(1, 7))


    # @classmethod
    # def ALIGNED_DAY_OF_WEEK_IN_MONTH(cls):
    #     return ChronoField('AlignedDayOfWeekInMonth',
    #                        ChronoUnit.DAYS(),
    #                        ChronoUnit.MONTHS(),
    #                        ValueRange.of(1, 7))
    # @classmethod
    # def ALIGNED_DAY_OF_WEEK_IN_YEAR(cls):
    #     return ChronoField('AlignedDayOfWeekInYear',
    #                        ChronoUnit.DAYS(),
    #                        ChronoUnit.WEEKS(),
    #                        ValueRange.of(1, 7))
    #
    # @classmethod
    # def DAY_OF_MONTH(cls):
    #     return ChronoField('DayOfMonth',
    #                        ChronoUnit.DAYS(),
    #                        ChronoUnit.MONTHS(),
    #                        ValueRange.of(1, 28, 31))
    #
    # @classmethod
    # def DAY_OF_YEAR(cls):
    #     return ChronoField('DayOfYear',
    #                        ChronoUnit.DAYS(),
    #                        ChronoUnit.YEARS(),
    #                        ValueRange.of(1, 365, 366))
    #
    # @classmethod
    # def EPOCH_DAY(cls):
    #     return ChronoField('EpochDay',
    #                        ChronoUnit.MICROS(),
    #                        ChronoUnit.SECONDS(),
    #                        ValueRange.of((long) (MIN_VALUE * 365.25), (long) (MAX_VALUE * 365.25)))
    #
    # @classmethod
    # def ALIGNED_WEEK_OF_MONTH(cls):
    #     return ChronoField('AlignedWeekOfMonth',
    #                        ChronoUnit.WEEKS(),
    #                        ChronoUnit.MONTHS(),
    #                        ValueRange.of(1, 4, 5)),
    #
    # @classmethod
    # def ALIGNED_WEEK_OF_YEAR(cls):
    #     return ChronoField('AlignedWeekOfYear',
    #                        ChronoUnit.WEEKS(),
    #                        ChronoUnit.YEARS(),
    #                        ValueRange.of(1, 53)),
    #
    # @classmethod
    # def MONTH_OF_YEAR(cls):
    #     return ChronoField('MonthOfYear',
    #                        ChronoUnit.MONTHS(),
    #                        ChronoUnit.YEARS(),
    #                        ValueRange.of(1, 12))
    #
    # @classmethod
    # def YEAR(cls):
    #     return ChronoField('Year',
    #                        ChronoUnit.YEARS(),
    #                        ChronoUnit.FOREVER(),
#                        ValueRange.of(MIN_VALUE, MAX_VALUE)
    #                        )
    # @classmethod
    # def INSTANT_SECONDS(cls):
    #     return ChronoField('InstantSeconds',
    #                        ChronoUnit.SECONDS(),
    #                        ChronoUnit.FOREVER(),
    #                        ValueRange.of(0x8000000000000000L, 0x7fffffffffffffffL)
    #                        )
    #
    # @classmethod
    # def OFFSET_SECONDS(cls):
    #     return ChronoField('OffsetSeconds',
    #                        ChronoUnit.SECONDS(),
    #                        ChronoUnit.FOREVER(),
    #                        ValueRange.of(-18 * 3600, 18 * 3600)
    #                        )

