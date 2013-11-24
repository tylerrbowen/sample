import re
from utils.bp.temporal.temporal_amount import TemporalAmount
from utils.bp.date_time_exception import DateTimeException
from utils.bp.duration import ChronoUnit
from utils.bp.chrono.chronology import Chronology


class Period(TemporalAmount):

    def __init__(self,
                 years,
                 months,
                 days):
        self._years = years
        self._months = months
        self._days = days

    @classmethod
    def ZERO(cls):
        return Period(0, 0, 0)

    @classmethod
    def PATTERN(cls):
        return re.compile('([-+]?)P(?:([-+]?[0-9]+)Y)?(?:([-+]?[0-9]+)M)?(?:([-+]?[0-9]+)D)?', re.IGNORECASE)

    @classmethod
    def of_years(cls, years):
        return Period(years, 0, 0)

    @classmethod
    def of_months(cls, months):
        return Period(0, months, 0)

    @classmethod
    def of_days(cls, days):
        return Period(0, 0, days)

    @classmethod
    def of(cls, years, months, days):
        return Period(years, months, days)

    @classmethod
    def between(cls, start_date, end_date):
        return start_date.period_until(end_date)

    @classmethod
    def parse(cls, text):
        matcher = cls.PATTERN().match(text)
        if matcher is not None:
            negate = -1 if '-' == matcher.group(1) else 1
            year_match = matcher.group(2)
            month_match = matcher.group(3)
            day_match = matcher.group(4)
            if year_match is not None or month_match is not None or day_match is not None:
                try:
                    return cls.create(cls.parse_number(text, year_match, negate),
                                      cls.parse_number(text, month_match, negate),
                                      cls.parse_number(text, day_match, negate))
                except Exception, e:
                    raise DateTimeException('Text cannot be parsed to a Period: ' + text)
        raise DateTimeException('Text cannot be parsed to a Period: ' + text)

    @classmethod
    def parse_number(cls, text, target_str, negate):
        if target_str is None:
            return 0
        val = int(target_str)
        try:
            return val * negate
        except ArithmeticError, e:
            raise DateTimeException('Text cannot be parsed to a Period: ' + text)

    @classmethod
    def create(cls, years, months, days):
        if (years | months | days) == 0:
            return cls.ZERO()
        return Period(years, months, days)


    def get_units(self):
        return set([ChronoUnit.YEARS, ChronoUnit.MONTHS, ChronoUnit.DAYS])

    def get(self, unit):
        if unit == ChronoUnit.YEARS:
            return self._years
        if unit == ChronoUnit.MONTHS:
            return self._months
        if unit == ChronoUnit.DAYS:
            return self._days
        raise DateTimeException('Unsupported unit: ' + unit.__str__())

    def is_zero(self):
        return self == self.ZERO()

    def is_negative(self):
        return  self._years < 0 or self._months < 0 or self._days < 0

    def get_years(self):
        return self._years

    def get_months(self):
        return self._months

    def get_days(self):
        return self._days

    def with_years(self, years):
        if years == self._years:
            return self
        return self.create(years, self._months, self._days)

    def with_months(self, months):
        if months == self._months:
            return self
        return self.create(self._years, months, self._days)

    def with_days(self, days):
        if days == self._days:
            return self
        return self.create(self._years, self._months, days)

    def plus(self, amount_to_add):
        return self.create(self._years + amount_to_add._years,
                           self._months + amount_to_add._months,
                           self._days + amount_to_add._days)

    def plus_years(self, years_to_add):
        return self.create(self._years + years_to_add, self._months, self._days)

    def plus_months(self, months_to_add):
        return self.create(self._years, self._months + months_to_add, self._days)

    def plus_days(self, days_to_add):
        return self.create(self._years, self._months, self._days + days_to_add)

    def minus(self, amount_to_subtract):
        return self.create(self._years - amount_to_subtract._years,
                           self._months - amount_to_subtract._months,
                           self._days - amount_to_subtract._days)

    def minus_years(self, years_to_subtract):
        return self.create(self._years - years_to_subtract, self._months, self._days)

    def minus_months(self, months_to_subtract):
        return self.create(self._years, self._months - months_to_subtract, self._days)

    def minus_days(self, days_to_subtract):
        return self.create(self._years, self._months, self._days - days_to_subtract)

    def multiplied_by(self, scalar):
        if self == self.ZERO() or scalar == 1:
            return self
        return self.create(self._years * scalar,
                           self._months * scalar,
                           self._days * scalar)

    def negated(self):
        return self.multiplied_by(-1)

    def normalized(self):
        total_months = self.to_total_months()
        split_years = total_months / 12
        split_months = total_months % 12
        if split_years == self._years and split_months == self._months:
            return self
        return self.create(int(split_years), split_months, self._days)

    def to_total_months(self):
        return self._years * 12L + self._months

    def add_to(self, temporal):
        if (self._years | self._months) != 0:
            month_range = self.month_range(temporal)
            if month_range >= 0:
                temporal = temporal.minus(self._years * month_range + self._months, ChronoUnit.MONTHS)
            else:
                if self._years != 0:
                    temporal = temporal.minus(self._years, ChronoUnit.YEARS)
                if self._months != 0:
                    temporal = temporal.minus(self._months, ChronoUnit.MONTHS)
        if self._days != 0:
            temporal = temporal.minus(self._days, ChronoUnit.DAYS)
        return temporal

    def month_range(self, temporal):
        start_range = Chronology.from_temporal(temporal).range(ChronoUnit.MONTHS)
        if start_range.is_fixed() and start_range.is_int_value():
            return start_range.get_maximum() - start_range.get_minimum()
        return -1

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, Period):
            return self._years == other._years and \
                self._months == other._months and \
                self._days == other._days
        return False

    def __hash__(self):
        return  self._years + (self._months << 8 | self._months >> -8) + (self._days << 16 | self._days >> -16)

    def __str__(self):
        if self == self.ZERO():
            return 'P0D'
        s = ''
        s += 'P'
        if self._years != 0:
            s += self._years.__str__() + 'Y'
        if self._months != 0:
            s += self._months.__str__() + 'M'
        if self._days != 0:
            s += self._days.__str__() + 'D'
        return s

