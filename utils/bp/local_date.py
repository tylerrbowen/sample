import datetime
from ids.comparable import Comparable
from utils.bp.clock import Clock
from utils.bp.duration import ChronoUnit, ChronoUnitItem
from utils.bp.local_time import LocalTime
from utils.bp.temporal.chrono_field import ChronoField, ChronoFieldItem
from temporal.value_range import ValueRange
from utils.bp.default.default_interface_temporal_accessor import DefaultInterfaceTemporalAccessor
from temporal.temporal import Temporal
from temporal.temporal_adjuster import TemporalAdjuster
from chrono.chrono_local_date import ChronoLocalDate
from temporal.temporal_queries import TemporalQueries
from date_time_exception import DateTimeException
from utils.bp.temporal.temporal import Temporal
from utils.bp.temporal.temporal_adjuster import TemporalAdjuster


class LocalDate(DefaultInterfaceTemporalAccessor, ChronoLocalDate):
    def __init__(self,
                 year,
                 month,
                 day_of_month):
        self._year = year
        self._month = month
        self._day = day_of_month

    @classmethod
    def MIN(cls):
        return LocalDate.of(Year.MIN_VALUE, 1, 1)

    @classmethod
    def MAX(cls):
        return LocalDate.of(Year.MAX_VALUE, 12, 31)

    @classmethod
    def DAYS_PER_CYCLE(cls):
        return 146097

    @classmethod
    def DAYS_0000_TO_1970(cls):
        return (cls.DAYS_PER_CYCLE() * 5L) - (30L * 365L + 7L)

    @classmethod
    def of(cls, year, month, day_of_month):
        """
        Obtains an instance of {@code LocalDate} from a year, month and day.
        @param year  the year to represent, from MIN_YEAR to MAX_YEAR
        @param month  the month-of-year to represent, from 1 (January) to 12 (December)
        @param dayOfMonth  the day-of-month to represent, from 1 to 31
        """
        ChronoField.YEAR.check_valid_value(year)
        ChronoField.MONTH_OF_YEAR.check_valid_value(month)
        ChronoField.DAY_OF_MONTH.check_valid_value(day_of_month)
        return LocalDate(year, month, day_of_month)

    @classmethod
    def of_year_day(cls, year, day_of_year):
        """
        Obtains an instance of {@code LocalDate} from a year and day-of-year.
        The day-of-year must be valid for the year, otherwise an exception will be thrown.
        """
        ChronoField.YEAR.check_valid_value(year)
        ChronoField.DAY_OF_YEAR.check_valid_value(day_of_year)
        leap = False#IsoChronology.INSTANCE().is_leap_year(year)
        if day_of_year == 366 and not leap:
            raise DateTimeException('Not leap year, given leap day')
        moy = 1#Month.of((day_of_year-1) / 31 + 1)
        month_end = moy.first_day_of_year(leap) + moy.length(leap) - 1
        if day_of_year > month_end:
            moy = moy.plus(1)
        dom = day_of_year - moy .first_day_of_year(leap) + 1
        return cls.create(year, moy, dom)

    @classmethod
    def of_epoch_day(cls, epoch_day):
        """
        Obtains an instance of {@code LocalDate} from the epoch day count.
        """
        zero_day = epoch_day + cls.DAYS_0000_TO_1970()
        zero_day -= 60
        adjust = 0
        if zero_day < 0:
            adjust_cyles = (zero_day + 1) / cls.DAYS_PER_CYCLE() - 1
            adjust = adjust_cyles * 400
            zero_day += -adjust_cyles * cls.DAYS_PER_CYCLE()
        year_est = (400 * zero_day + 591) / cls.DAYS_PER_CYCLE()
        doy_est = zero_day - (365 * year_est + year_est / 4 - year_est / 100 + year_est / 400)
        if doy_est < 0:
            year_est -= 1
            doy_est = zero_day - (365 * year_est + year_est / 4 - year_est / 100 + year_est /400)
        year_est += adjust
        march_doy_0 = int(doy_est)

        march_month_0 = (march_doy_0 * 5 + 2) / 153
        month = (march_month_0 + 2) % 12 + 1
        dom = march_doy_0 - (march_month_0 * 306 + 5) / 10 + 1
        year_est += march_month_0 / 10
        year = ChronoField.YEAR.check_valid_int_value(year_est)
        return LocalDate(year, month, dom)

    @classmethod
    def from_temporal(cls, temporal):
        date = temporal.query(TemporalQueries.local_date())
        if date is None:
            raise DateTimeException("Unable to obtain LocalDate from TemporalAccessor: " + temporal.__class__.__name__)
        return date

    @classmethod
    def parse(cls, text, formatter=None):
        datetimedate = datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        return LocalDate(datetimedate.year, datetimedate.month, datetimedate.day)

    @classmethod
    def create(cls, year, month, day_of_month):
        """
        year: int
        month: Month
        day_of_month: int
        """
        # if day_of_month > 28 and day_of_month > month.length(IsoChronology.INSTANCE().is_leap_year()):
        #     if day_of_month == 29:
        #         raise DateTimeException('Invalid leap day for year')
        #     else:
        #         raise DateTimeException('Invalid Date')
        # return LocalDate(year, month.get_value(), day_of_month)
        pass

    @classmethod
    def resolve_previous_valid(cls, year, month, day):
        # if month == 2:
        #     day = min(day, 29 if IsoChronology.INSTANCE().is_leap_year() else 28)
        # elif month == 4 or month == 6 or month == 9 or month == 12:
        #     day = min(day, 30)
        # return LocalDate.of(year, month, day)
        pass

    def is_supported(self, field):
        return super(LocalDate, self).is_supported(field)

    def range(self, field):
        if isinstance(field, ChronoFieldItem):
            f = field
            if f.is_date_field():
                if f == ChronoField.DAY_OF_MONTH:
                    return ValueRange.of(1, self.length_of_month())
                elif f == ChronoField.DAY_OF_YEAR:
                    return ValueRange.of(1, self.length_of_year())
                elif f == ChronoField.ALIGNED_WEEK_OF_MONTH:
                    #if self.get_month() == Month.FEBRUARY and not self.is_leap_year():
                    if False:
                        return ValueRange.of(1, 4)
                    else:
                        return ValueRange.of(1, 5)
                elif f == ChronoField.YEAR_OF_ERA:
                    if self.get_year() <= 0:
                        return ValueRange.of(1, Year.MAX_VALUE + 1)
                    else:
                        return ValueRange.of(1, Year.MAX_VALUE)
                return field.range()
            raise DateTimeException('Unsupported Field: ' + field.get_name())
        return field.range_refined_by(self)

    def get(self, field):
        if isinstance(field, ChronoFieldItem):
            return self.get0(field)
        return super(LocalDate, self).get(field)

    def get_chronology(self):
        pass

    def get_long(self, field):
        if isinstance(field, ChronoFieldItem):
            if field == ChronoField.EPOCH_DAY:
                return self.to_epoch_day()
            if field == ChronoField.EPOCH_MONTH:
                return self.get_epoch_month()
            return self.get0(field)
        return field.get_from(self)

    def get0(self, field):
        if field == ChronoField.DAY_OF_WEEK:
            return self.get_day_of_week().get_value()
        elif field == ChronoField.ALIGNED_DAY_OF_WEEK_IN_MONTH:
            return ((self.day - 1) % 7) + 1
        elif field == ChronoField.ALIGNED_DAY_OF_WEEK_IN_YEAR:
            return ((self.get_day_of_year() -1) % 7) + 1
        elif field == ChronoField.DAY_OF_MONTH:
            return self._day
        elif field == ChronoField.DAY_OF_YEAR:
            return self.get_day_of_year()
        elif field == ChronoField.EPOCH_DAY:
            raise DateTimeException()
        elif field == ChronoField.ALIGNED_WEEK_OF_MONTH:
            return ((self._day - 1) / 7) + 1
        elif field == ChronoField.MONTH_OF_YEAR:
            return self._month
        elif field == ChronoField.EPOCH_MONTH:
            raise DateTimeException()
        elif field == ChronoField.YEAR_OF_ERA:
            return self._year if self._year >= 1 else 1 - self._year
        elif field == ChronoField.ERA:
            return 1 if self._year >= 1 else 0
        raise DateTimeException('unsupported field ' + field.get_name())

    def get_epoch_month(self):
        return ((self._year - 1970) * 12L) + (self._month - 1)

    def get_chnorology(self):
        #return IsoChronology.INSTANCE()
        pass

    def get_era(self):
        return super(LocalDate, self).get_era()

    def get_year(self):
        return self._year

    def get_month_value(self):
        return self._month

    def get_month(self):
        #return  Month.of(self._month)
        return 1

    def get_day_of_month(self):
        return self._day

    def get_day_of_year(self):
        return self.get_month().first_day_of_year(self.is_leap_year()) + self._day - 1

    def get_day_of_week(self):
        dow0 = (self.to_epoch_day() + 3) % 7
        #return DayOfWeek.of(dow0 + 1)

    def is_leap_year(self):
        return self._year & 3 == 0 and (self._year & 100 != 0 or self._year & 400 == 0)

    def length_of_month(self):
        if self._month == 2:
            return 29 if self.is_leap_year() else 28
        elif self._month == 4 or \
                self._month == 6 or \
                self._month == 9 or \
                self._month == 11:
            return 30
        return 31

    def length_of_year(self):
        return 366 if self.is_leap_year() else 365

    def with_adjuster(self, adjuster):
        if isinstance(adjuster, LocalDate):
            return adjuster
        return adjuster.adjust_into(self)

    def with_field(self, field, new_value):
        if isinstance(field, ChronoFieldItem):
            f = field
            f.check_valid_value(new_value)
            if f == ChronoField.DAY_OF_WEEK:
                return self.plus_days(new_value - self.get_day_of_week().get_value())
            elif f == ChronoField.ALIGNED_DAY_OF_WEEK_IN_MONTH:
                return self.plus_days(new_value - self.get_long(ChronoField.ALIGNED_DAY_OF_WEEK_IN_MONTH))
            elif f == ChronoField.ALIGNED_DAY_OF_WEEK_IN_YEAR:
                return self.plus_days(new_value - self.get_long(ChronoField.ALIGNED_DAY_OF_WEEK_IN_YEAR))
            elif f == ChronoField.DAY_OF_MONTH:
                return self.with_day_of_month(int(new_value))
            elif f == ChronoField.DAY_OF_YEAR:
                return self.with_day_of_year(int(new_value))
            elif f == ChronoField.EPOCH_DAY:
                return LocalDate.of_epoch_day(new_value)
            elif f == ChronoField.ALIGNED_WEEK_OF_MONTH:
                return self.plus_weeks(new_value - self.get_long(ChronoField.ALIGNED_WEEK_OF_MONTH))
            elif f == ChronoField.ALIGNED_WEEK_OF_YEAR:
                return self.plus_weeks(new_value - self.get_long(ChronoField.ALIGNED_WEEK_OF_YEAR))
            elif f == ChronoField.MONTH_OF_YEAR:
                return self.with_month(new_value)
            elif f == ChronoField.EPOCH_MONTH:
                return self.plus_months(new_value - self.get_long(ChronoField.EPOCH_MONTH))
            elif f == ChronoField.YEAR_OF_ERA:
                return self.with_year(new_value if self._year >= 1 else 1 - new_value)
            elif f == ChronoField.YEAR:
                return self.with_year(new_value)
            elif f == ChronoField.ERA:
                return self if self.get_long(ChronoField.ERA) == new_value else self.with_year(1 - self._year)
            raise DateTimeException('exception')
        return field.adjust_into(self, new_value)

    def with_year(self, year):
        if self._year == year:
            return self
        ChronoField.YEAR.check_valid_value(year)
        return self.resolve_previous_valid(year, self._month, self._day)

    def with_month(self, month):
        if self._month == month:
            return self
        ChronoField.MONTH_OF_YEAR.check_valid_value(month)
        return self.resolve_previous_valid(self._year, month, self._day)

    def with_day_of_month(self, day_of_month):
        if self._day == day_of_month:
            return self
        ChronoField.DAY_OF_MONTH.check_valid_value(day_of_month)
        return self.of(self._year, self._month, day_of_month)

    def with_day_of_year(self, day_of_year):
        if self.get_day_of_year() == day_of_year:
            return self
        return self.of_year_day(self._year, day_of_year)

    def plus_temporal(self, temporal_amount):
        return temporal_amount.add_to(self)

    def plus(self, amount_to_add=None, unit=None):
        if isinstance(unit, ChronoUnitItem):
            f = unit
            if f == ChronoUnit.DAYS:
                return self.plus_days(amount_to_add)
            elif f == ChronoUnit.WEEKS:
                return self.plus_weeks(amount_to_add)
            elif f == ChronoUnit.MONTHS:
                return self.plus_months(amount_to_add)
            elif f == ChronoUnit.YEARS:
                return self.plus_years(amount_to_add)
            elif f == ChronoUnit.DECADES:
                return self.plus_years(amount_to_add * 10)
            elif f == ChronoUnit.CENTURIES:
                return self.plus_years(amount_to_add * 100)
            elif f == ChronoUnit.MILLENNIA:
                return self.plus_years(amount_to_add * 1000)
            elif f == ChronoUnit.ERAS:
                return self.with_field(ChronoField.ERA, amount_to_add)
            raise DateTimeException()
        return unit.add_to(self, amount_to_add)

    def plus_years(self, years_to_add):
        if years_to_add == 0:
            return self
        new_year = ChronoField.YEAR.check_valid_int_value(years_to_add + self._year)
        return self.resolve_previous_valid(new_year, self._month, self._day)

    def plus_months(self, months_to_add):
        if months_to_add == 0:
            return self
        month_count = self._year * 12L + (self._month - 1)
        calc_months = month_count + months_to_add
        new_year = ChronoField.YEAR.check_valid_int_value(calc_months // 12)
        new_month = calc_months // 12 + 1
        return self.resolve_previous_valid(new_year, new_month, self._day)

    def plus_weeks(self, weeks_to_add):
        return self.plus_days(weeks_to_add * 7)

    def plus_days(self, days_to_add):
        if days_to_add == 0:
            return self
        mj_day = self.to_epoch_day() + days_to_add
        return LocalDate.of_epoch_day(mj_day)

    def minus_temporal(self, temporal_amount):
        return temporal_amount.subtract_from(self)

    def minus(self, amount=None, unit=None):
        if amount == 0x8000000000000000L:
            return self.plus(0x7fffffffffffffffL, unit).plus(1, unit)
        else:
            return self.plus(-amount, unit)

    def minus_years(self, years_to_subtract):
        if years_to_subtract == 0x8000000000000000L:
            return self.plus_years(0x7fffffffffffffffL).plus_years(1)
        else:
            return self.plus_years(-years_to_subtract)

    def minus_months(self, months_to_subtract):
        if months_to_subtract == 0x8000000000000000L:
            return self.plus_months(0x7fffffffffffffffL).plus_months(1)
        else:
            return self.plus_months(-months_to_subtract)

    def minus_weeks(self, weeks_to_subtract):
        if weeks_to_subtract == 0x8000000000000000L:
            return self.plus_months(0x7fffffffffffffffL).plus_weeks(1)
        else:
            return self.plus_weeks(-weeks_to_subtract)

    def minus_days(self, days_to_subtract):
        if days_to_subtract == 0x8000000000000000L:
            return self.plus_days(0x7fffffffffffffffL).plus_days(1)
        else:
            return self.plus_days(-days_to_subtract)

    def query(self, query):
        if query == TemporalQueries.local_date():
            return self
        return super(LocalDate, self).query(query)

    def adjust_into(self, temporal):
        return super(LocalDate, self).adjust_into(temporal)

    def period_until(self, end_temporal, unit):
        if not isinstance(end_temporal, LocalDate):
            raise DateTimeException
        end = end_temporal
        if isinstance(unit, ChronoUnitItem):
            if unit == ChronoUnit.DAYS:
                return self.days_until(end)
            if unit == ChronoUnit.WEEKS:
                return self.days_until(end) / 7
            if unit == ChronoUnit.MONTHS:
                return self.months_until(end)
            if unit == ChronoUnit.YEARS:
                return self.months_until(end) / 12
            if unit == ChronoUnit.DECADES:
                return self.months_until(end) / 120
            if unit == ChronoUnit.CENTURIES:
                return self.months_until(end) / 1200
            if unit == ChronoUnit.MILLENNIA:
                return self.months_until(end) / 12000
            if unit == ChronoUnit.ERAS:
                return end.get_long(ChronoField.ERA) - self.get_long(ChronoField.ERA)
            raise DateTimeException
        return unit.between(self, end_temporal)

    def days_until(self, end):
        return end.to_epoch_day() - self.to_epoch_day()

    def months_until(self, end):
        packed1 = self.get_epoch_month() * 32L + self.get_day_of_month()
        packed2 = end.get_epoch_month() * 32L + end.get_day_of_month()
        return (packed2 - packed1) / 32

    def period_until_date(self, end_date):
        end = LocalDate.from_temporal(end_date)
        total_months = end.get_epoch_month() - self.get_epoch_month()
        days = end._day - self._day
        if total_months > 0 and days < 0:
            total_months -= 1
            calc_date = self.plus_months(total_months)
            days = int(end.to_epoch_day() - calc_date.to_epoch_day())
        elif total_months < 0 and days > 0:
            total_months += 1
            days -= end.length_of_month()

        years = total_months / 12
        months = int(total_months % 12)
        #return Period.of(years, months, days)

    def at_time(self, time):
        #return LocalDateTime.of(self, time)
        pass

    def at_hours_minutes(self, hour, minute, second=0, nano_of_second=0):
        return self.at_time(LocalTime.of(hour, minute, second, nano_of_second))

    def at_offset_time(self, time):
        #return OffsetDateTime.of(LocalDateTime.of(self, time.to_local_time()), time.get_offset())
        pass

    def local_at_start_of_day(self):
        #return LocalDateTime.of(self, LocalTime.MIDNIGHT())
        pass

    def zone_at_start_of_day(self, zone):
        dt_ = datetime.datetime(self._year, self._month, self._day, tzinfo='UTC')
        #ldt = self.at_time(LocalTime.MIDNIGHT())
        # if not isinstance(zone, ZoneOffset):
        #     rulse = zone.get_rules()
        #     trans = rules.get_transition(ldt)
        #     if trans is not None and trans.is_gap():
        #         ldt = trans.get_date_time_after()
        # return ZoneDateTime.of(ldt, zone)
        return dt_

    def to_epoch_day(self):
        y = self._year
        m = self._month
        total = 0
        total += 365 * y
        if y >= 0:
            total += (y + 3) / 4 - (y + 99) / 100 + (y + 399) / 400
        else:
            total -= y / -4 - y / -100 + y / -400
        total += ((367 * m - 362) / 12)
        total += self._day - 1
        if m > 2:
            total -= 1
            if not self.is_leap_year():
                total -= 1
        return total - self.DAYS_0000_TO_1970()

    def __cmp__(self, other):
        if isinstance(other, LocalDate):
            return self.compare_to_0(other)
        return super(LocalDate, self).__cmp__(other)

    def compare_to_0(self, other):
        comp = self._year - other._year
        if comp == 0:
            comp = self._month - other._month
            if comp == 0:
                comp = self._day - other._day
        return comp

    def is_after(self, other):
        if isinstance(other, LocalDate):
            return self.compare_to_0(other) > 0
        return super(LocalDate, self).is_after(other)

    def is_before(self, other):
        if isinstance(other, LocalDate):
            return self.compare_to_0(other) < 0
        return super(LocalDate, self).is_before(other)

    def is_equal(self, other):
        if isinstance(other, LocalDate):
            return self.compare_to_0(other) == 0
        return super(LocalDate, self).is_equal(other)

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, LocalDate):
            return self.compare_to_0(other) == 0
        return False

    def __hash__(self):
        year = self._year
        month = self._month
        day = self._day
        return (year & 0xFFFFF800) ^ ((year << 11) + (month << 6) + (day))


    def __str__(self):
        year = self._year
        month = self._month
        day = self._day
        abs_year = abs(year)
        buf = ''
        if abs_year < 1000:
            if year < 0:
                buf += (year - 10000).__str__()
                buf = buf[0] + buf[2:]
            else:
                buf += (year + 10000).__str__()
                buf = buf[0] + buf[2:]
        else:
            if year > 9999:
                buf += '+'
            buf += year.__str__()
        buf += '-0' if month < 10 else '-'
        buf += month.__str__()
        buf += '-0' if day < 10 else '-'
        buf += day.__str__()
        return buf




    @classmethod
    def now(cls, clock):
        now = clock.instant()
        offset = clock.get_zone().get_rules().get_offset(now)
        epoch_sec = now.get_epoch_second() + offset.get_total_seconds()
        epoch_day = epoch_sec // LocalTime.SECONDS_PER_DAY
        return LocalDate.of_epoch_day(epoch_day)


class Year(DefaultInterfaceTemporalAccessor, Temporal, TemporalAdjuster, Comparable):
    MIN_VALUE = -999999999
    MAX_VALUE = 999999999

    def __init__(self):
        self._year = None

    def now(self, clock=None, zone=None):
        if clock is None and zone is None:
            clock = Clock.system(Clock.system_default_zone())
        elif zone is not None and clock is None:
            clock = Clock.system(zone)
        now = LocalDate.now(clock)
        return Year.of(now.get_year())