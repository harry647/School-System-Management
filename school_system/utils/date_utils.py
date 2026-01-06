"""
Date Utilities

This module provides utility functions for working with dates and times,
including formatting, parsing, and date calculations.
"""

import datetime
import time
from typing import Optional, Tuple, Union
from dateutil.relativedelta import relativedelta
import pytz


class DateUtils:
    """A utility class for working with dates and times."""

    @staticmethod
    def get_current_date() -> str:
        """
        Get the current date in YYYY-MM-DD format.

        Returns:
            Current date as a string in YYYY-MM-DD format
        """
        return datetime.datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def get_current_datetime() -> str:
        """
        Get the current date and time in ISO format.

        Returns:
            Current date and time as a string in ISO format
        """
        return datetime.datetime.now().isoformat()

    @staticmethod
    def get_current_timestamp() -> int:
        """
        Get the current Unix timestamp.

        Returns:
            Current Unix timestamp as an integer
        """
        return int(time.time())

    @staticmethod
    def format_date(
        date: Union[str, datetime.datetime], 
        format_str: str = '%Y-%m-%d'
    ) -> str:
        """
        Format a date according to the specified format.

        Args:
            date: Date to format (string or datetime object)
            format_str: Format string for the output

        Returns:
            Formatted date string

        Raises:
            ValueError: If the date string cannot be parsed
        """
        if isinstance(date, str):
            # Try to parse the date string
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj.strftime(format_str)

    @staticmethod
    def parse_date(
        date_str: str, 
        format_str: Optional[str] = None
    ) -> datetime.datetime:
        """
        Parse a date string into a datetime object.

        Args:
            date_str: Date string to parse
            format_str: Optional format string for parsing

        Returns:
            Parsed datetime object

        Raises:
            ValueError: If the date string cannot be parsed
        """
        if format_str:
            return datetime.datetime.strptime(date_str, format_str)
        else:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Could not parse date: {date_str}")

    @staticmethod
    def add_days(date: Union[str, datetime.datetime], days: int) -> datetime.datetime:
        """
        Add days to a date.

        Args:
            date: Date to modify (string or datetime object)
            days: Number of days to add

        Returns:
            New datetime object with days added
        """
        if isinstance(date, str):
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj + datetime.timedelta(days=days)

    @staticmethod
    def add_months(date: Union[str, datetime.datetime], months: int) -> datetime.datetime:
        """
        Add months to a date.

        Args:
            date: Date to modify (string or datetime object)
            months: Number of months to add

        Returns:
            New datetime object with months added
        """
        if isinstance(date, str):
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj + relativedelta(months=months)

    @staticmethod
    def add_years(date: Union[str, datetime.datetime], years: int) -> datetime.datetime:
        """
        Add years to a date.

        Args:
            date: Date to modify (string or datetime object)
            years: Number of years to add

        Returns:
            New datetime object with years added
        """
        if isinstance(date, str):
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj + relativedelta(years=years)

    @staticmethod
    def get_date_difference(
        date1: Union[str, datetime.datetime], 
        date2: Union[str, datetime.datetime]
    ) -> Tuple[int, int, int]:
        """
        Calculate the difference between two dates.

        Args:
            date1: First date (string or datetime object)
            date2: Second date (string or datetime object)

        Returns:
            Tuple of (days, months, years) difference
        """
        if isinstance(date1, str):
            date1 = DateUtils.parse_date(date1)
        if isinstance(date2, str):
            date2 = DateUtils.parse_date(date2)

        delta = relativedelta(date2, date1)
        return delta.days, delta.months, delta.years

    @staticmethod
    def get_age(birth_date: Union[str, datetime.datetime]) -> int:
        """
        Calculate age from birth date.

        Args:
            birth_date: Birth date (string or datetime object)

        Returns:
            Age in years
        """
        if isinstance(birth_date, str):
            birth_date = DateUtils.parse_date(birth_date)

        today = datetime.datetime.now()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    @staticmethod
    def is_weekend(date: Union[str, datetime.datetime]) -> bool:
        """
        Check if a date falls on a weekend.

        Args:
            date: Date to check (string or datetime object)

        Returns:
            True if the date is on a weekend, False otherwise
        """
        if isinstance(date, str):
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday

    @staticmethod
    def get_day_of_week(date: Union[str, datetime.datetime]) -> str:
        """
        Get the name of the day of the week.

        Args:
            date: Date to check (string or datetime object)

        Returns:
            Name of the day (e.g., "Monday")
        """
        if isinstance(date, str):
            date_obj = DateUtils.parse_date(date)
        else:
            date_obj = date

        return date_obj.strftime('%A')

    @staticmethod
    def convert_timezone(
        dt: Union[str, datetime.datetime], 
        from_tz: str = 'UTC',
        to_tz: str = 'local'
    ) -> datetime.datetime:
        """
        Convert a datetime between timezones.

        Args:
            dt: Datetime to convert (string or datetime object)
            from_tz: Source timezone
            to_tz: Target timezone

        Returns:
            Datetime object in the target timezone
        """
        if isinstance(dt, str):
            dt = DateUtils.parse_date(dt)

        # Make the datetime timezone-aware
        if dt.tzinfo is None:
            from_zone = pytz.timezone(from_tz)
            dt = from_zone.localize(dt)
        else:
            from_zone = dt.tzinfo

        if to_tz.lower() == 'local':
            to_zone = pytz.timezone('Africa/Nairobi')  # User's timezone
        else:
            to_zone = pytz.timezone(to_tz)

        return dt.astimezone(to_zone)