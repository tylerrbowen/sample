import datetime
import pytz
from utils.argument_checker import ArgumentChecker, IllegalArgumentException
from utils.bp.instant import Instant
from utils.bp.zoned_date_time import ZonedDateTime
from utils.bp.local_date import LocalDate
from utils.bp.local_date_time import LocalDateTime
from utils.bp.local_time import LocalTime


class DateUtils:
    """
    Utility class for dates.
    """

    SECONDS_PER_DAY = 60 * 60 * 24
    DAYS_PER_YEAR = 365.25
    MILLISECONDS_PER_DAY = SECONDS_PER_DAY * 1000
    SECONDS_PER_YEAR = int(SECONDS_PER_DAY * DAYS_PER_YEAR)
    MILLISECONDS_PER_YEAR = SECONDS_PER_YEAR * 1000

    @classmethod
    def get_difference_in_years(cls, start_date, end_date):
        """
        Returns endDate - startDate in years, where a year is defined as 365.25 days.
        @param startDate the start date, not null
        @param endDate the end date, not null
        @return the difference in years
        @throws IllegalArgumentException if either date is null
        """
        if start_date is None:
            raise IllegalArgumentException('Start Date Null')
        if end_date is None:
            raise IllegalArgumentException('End Date Null')
        return (end_date._date_time._date.to_epoch_day() - start_date._date_time._date.to_epoch_day()) / (cls.DAYS_PER_YEAR + 0.)

    @classmethod
    def get_date_offset_with_year_fraction(cls, start_date, year_fraction):
        instant = Instant.from_dt_datetime(
            datetime.datetime(
                start_date.get_year(), start_date.get_month(), start_date.get_day_of_month())
        )
        nanos = int(round(1000000000 * cls.SECONDS_PER_YEAR * year_fraction))
        offset_date = instant.plus_nanos(nanos)
        return ZonedDateTime.of_instant(offset_date, 'UTC')#start_date.get_zone())

    @classmethod
    def get_utc_date(cls, year, month, day):
        instant = Instant.from_dt_datetime(
            datetime.datetime(
                year, month, day)
        )
        offset_date = instant
        return ZonedDateTime.of_instant(offset_date, 'UTC')
