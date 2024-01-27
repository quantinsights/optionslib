"""A module offering various helper functions to work with discount factors, dates
etc."""

import calendar
import datetime as dt

from optionslib.types.enums import BusinessDayConventions, DayOfWeek, Period


def is_leap_year(year: int) -> bool:
    """Test if the given year is a leap year."""
    return (year % 4 == 0 and not year % 100 == 0) or (year % 400 == 0)


def length_of_year(year: int) -> int:
    """Returns the number of days in a year."""
    return 366 if is_leap_year(year) else 365


def ensure_leap_year(date_value: dt.date) -> dt.date:
    """Returns the 29th of February if the current year is a leap year, else looks for
    the next near nearest 29th Feb."""
    for year_delta in range(5):
        candidate_year = date_value.year + year_delta
        if is_leap_year(candidate_year):
            return dt.date(candidate_year, 2, 29)
    raise ValueError(f"Given date is not handled properly {date_value=}")


def next_leap_day(date_value: dt.date) -> dt.date:
    """Returns the next leap date."""
    # Handle if already a leap day, move forward either 4 or 8 years.
    if date_value.month == 2 and date_value.day == 29:
        if is_leap_year(date_value.year):
            return ensure_leap_year(
                dt.date(date_value.year + 4, date_value.month, date_value.day)
            )

    # Handle if before February in a leap year.
    if date_value.month <= 2 and is_leap_year(date_value.year):
        return dt.date(date_value.year, 2, 29)

    # Handle any other date
    yy = (date_value.year // 4) * 4
    return ensure_leap_year(dt.date(yy + 4, 2, 29))


def get_length_of_month(date_value: dt.date) -> int:
    """Returns the number of days in a month."""
    _, num_days = calendar.monthrange(date_value.year, date_value.month)
    return num_days


def first_in_month(year: int, month: int, day_of_week: DayOfWeek):
    """Returns the first day_of_week in the month."""
    first_of_month = dt.date(year, month, 1)
    result = first_of_month

    while result.weekday() != day_of_week:
        result = result + dt.timedelta(days=1)

    return result


def last_in_month(year: int, month: int, day_of_week: DayOfWeek):
    """Returns the last day_of_week in the given month."""
    first_of_month = dt.date(year, month, 1)
    num_days = get_length_of_month(first_of_month)
    end_of_month = dt.date(year, month, num_days)
    result = end_of_month

    while result.weekday() != day_of_week:
        result = result - dt.timedelta(days=1)
    return result


def easter(year: int) -> dt.date:
    """
    Butcher's algorithm to calculate the Easter day of any given year.

    Reference. https://en.wikipedia.org/wiki/Date_of_Easter

    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = b - f + 1
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    dd = ((h + l - 7 * m + 114) % 31) + 1

    return dt.date(year, month, dd)


def bump_sun_to_mon(date_value: dt.date) -> dt.date:
    """Bumps to monday, if the given date falls on a sunday."""
    if date_value.weekday() == DayOfWeek.SUNDAY:
        return date_value + dt.timedelta(days=1)

    return date_value


def bump_to_mon(date_value: dt.date) -> dt.date:
    """Bumps to monday, if the given date falls on a weekend."""
    match date_value.weekday():
        case DayOfWeek.SATURDAY:
            return date_value + dt.timedelta(days=2)
        case DayOfWeek.SUNDAY:
            return date_value + dt.timedelta(days=1)
        case _:
            return date_value


def bump_to_fri_or_mon(date_value: dt.date) -> dt.date:
    """Bumps saturday to friday and sunday to monday."""
    match date_value.weekday():
        case DayOfWeek.SATURDAY:
            return date_value - dt.timedelta(days=1)
        case DayOfWeek.SUNDAY:
            return date_value + dt.timedelta(days=1)
        case _:
            return date_value


def christmas_bumped_sat_or_sun(year: int) -> dt.date:
    """If Christmas falls on saturday or sunday, move to 27th December."""
    base = dt.date(year, 12, 25)
    if base.weekday() in (DayOfWeek.SATURDAY, DayOfWeek.SUNDAY):
        return dt.date(year, 12, 27)
    return base


def christmas_bumped_sun(year: int) -> dt.date:
    """If Christmas is on sunday, moved to Monday."""
    base = dt.date(year, 12, 25)
    if base.weekday() is DayOfWeek.SUNDAY:
        return dt.date(year, 12, 26)
    return base


def boxing_day_bumped_sun(year: int) -> dt.date:
    """Boxing day (if Christmas is sunday, boxing day moved from Monday to Tuesday)"""
    base = dt.date(year, 12, 26)
    if base.weekday() is DayOfWeek.MONDAY:
        return dt.date(year, 12, 27)
    return base


def boxing_day_bumped_sat_sun(year: int) -> dt.date:
    """If boxing day is on saturday(sunday), bumped to monday(tuesday)"""
    base = dt.date(year, 12, 26)
    if base.weekday() in (DayOfWeek.SATURDAY, DayOfWeek.SUNDAY):
        return dt.date(year, 12, 28)
    return base


def add_months(start: dt.date, months: int) -> dt.date:
    """Add months to a date."""
    year_roll = (start.month + months - 1) // 12
    month = (start.month + months) % 13 + year_roll
    try:
        end = dt.date(start.year + year_roll, month, start.day)
    except ValueError:  # day is out of range for the month
        return add_months(dt.date(start.year, start.month, start.day - 1), months)
    return end


def add_years(start: dt.date, years: int) -> dt.date:
    """Add years to a date."""
    try:
        end = dt.date(start.year + years, start.month, start.day)
    except ValueError:
        return add_years(dt.date(start.year, start.month, start.day - 1), years)
    return end


def add_period(start: dt.date, length: int, period: Period, holiday_calendar):
    """Add period of a certain length to a date."""
    match period:
        case Period.YEARS:
            return add_years(start, years=length)
        case Period.MONTHS:
            return add_months(start, months=length)
        case Period.DAYS:
            return start + dt.timedelta(days=length)
        case Period.BUSINESS_DAYS:
            if not length:
                return start
            next_date = start + dt.timedelta(days=1 if length > 0 else -1)
            if holiday_calendar.is_holiday(next_date):
                return add_period(
                    next_date,
                    length,
                    Period.BUSINESS_DAYS,
                    holiday_calendar,
                )
            return add_period(
                next_date,
                length + (-1 if length > 0 else +1),
                Period.BUSINESS_DAYS,
                holiday_calendar,
            )
        case _:
            raise ValueError(f"Incompatible {period=}.")


def adjust(
    unadjusted_date: dt.date,
    bus_day_convention: BusinessDayConventions,
    holiday_calendar,
) -> dt.date:
    """
    Converts an undajusted date to an adjusted date.

    Ref. https://en.wikipedia.org/wiki/Date_rolling

    """
    if not holiday_calendar.is_holiday(unadjusted_date):
        return unadjusted_date

    following_date = add_period(
        unadjusted_date, 1, Period.BUSINESS_DAYS, holiday_calendar
    )
    preceding_date = add_period(
        unadjusted_date, -1, Period.BUSINESS_DAYS, holiday_calendar
    )
    match bus_day_convention:
        case BusinessDayConventions.NO_ADJUST:
            return unadjusted_date
        case BusinessDayConventions.FOLLOWING:
            return following_date
        case BusinessDayConventions.PRECEDING:
            return preceding_date
        case BusinessDayConventions.MODIFIED_FOLLOWING:
            return (
                following_date
                if following_date.month == unadjusted_date.month
                else preceding_date
            )
        case BusinessDayConventions.MODIFIED_PRECEDING:
            return (
                preceding_date
                if following_date.month == unadjusted_date.month
                else following_date
            )
        case _:
            raise ValueError(f"Incompatible {bus_day_convention=}.")
