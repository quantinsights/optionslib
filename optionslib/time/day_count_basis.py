"""Module to support various day count conventions.

Reference.  https://en.wikipedia.org/wiki/Day_count_convention.
"""

import datetime as dt
from abc import ABC, abstractmethod

from optionslib.time import time_utils


class DayCountBase(ABC):
    """An abstract class that serves as the base class for all day-count
    conventions."""

    @staticmethod
    def days_between(start_inclusive: dt.date, end_exlusive: dt.date):
        """Returns the number of calendar days in the period
        [startInclusive,endExclusive)."""
        return (end_exlusive - start_inclusive).days

    @staticmethod
    @abstractmethod
    def year_fraction(d_1: dt.date, d_2: dt.date) -> float:
        """Each child class must provide an implementation of the
        year_fraction() method."""
        pass


class Actual360(DayCountBase):
    """An implementation of the ACT/360 day-count convention."""

    @staticmethod
    def year_fraction(d_1: dt.date, d_2: dt.date) -> float:
        return DayCountBase.days_between(d_1, d_2) / 360


class Actual365(DayCountBase):
    """An implementation of the ACT/365 day-count convention."""

    @staticmethod
    def year_fraction(d_1: dt.date, d_2: dt.date) -> float:
        return DayCountBase.days_between(d_1, d_2) / 365


class ActualActual(DayCountBase):
    """Returns the year fraction between [d1,d2) in the ACT/ACT day count
    convention.

    ACT/ACT assumes that a year consists of 365 or 366 days (in case of a leap year), and that the days
    between dates s and t, s prior to t, are counted as the actual number of calendar days between the two
    dates, including the first but not the second.

    If s and t are dates belonging to the same year and n is the actual number of days in the year, then the
    year fraction equals (t - s).

    If s and t are dates belonging to two different years, let J_i be the first of January of the second year,
    J_f be the first of January of the final year, n_i be the number of days in the first year, n_f be the number
    of days of the final year, and y the number of years between the first and the final year, then the year
    fraction equals
    (J_i - s)/n_i + y + (t - J_f)/n_f
    """

    @staticmethod
    def year_fraction(d_1: dt.date, d_2: dt.date) -> float:
        """Returns the actual/actual year fraction."""
        y_1 = d_1.year
        y_2 = d_2.year

        if y_1 == y_2:
            return (d_2 - d_1).days / utils.length_of_year(y_1)
        else:
            j_i = dt.date(y_1 + 1, 1, 1)
            j_f = dt.date(y_2, 1, 1)
            n_i = utils.length_of_year(y_1)
            n_f = utils.length_of_year(y_2)
            y = y_2 - y_1
            return (j_i - d_1).days / n_i + y + (d_2 - j_f).days / n_f


class Thirty360(DayCountBase):
    """An implementation of the 30/360 day count convention."""

    @staticmethod
    def year_fraction(d_1: dt.date, d_2: dt.date) -> float:
        """Returns the 30/360 year fraction."""
        start_date = d_1
        end_date = d_2

        if d_2.day == 31 and d_1.day > 29:
            end_date = dt.date(d_2.year, d_2.month, 30)

        if d_1.day == 31:
            start_date = dt.date(d_1.year, d_1.month, 30)

        return (
            360 * (end_date.year - start_date.year)
            + 30 * (end_date.month - start_date.month)
            + (end_date.day - start_date.day)
        ) / 360
