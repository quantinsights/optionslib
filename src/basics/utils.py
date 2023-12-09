from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import calendar

from src.basics.day_count_basis import Actual360, Actual365, ActualActual
from src.basics.enums import DayOfWeek


def df_to_zero(df: float, t_1:dt.date, t_2:dt.date) -> float:
    """
    Converts the discount factor P(t,T) to the annually compounded spot interest rate Y(t,T).
    """
    tau = Actual365.year_fraction(t_1, t_2)
    if tau == 0.0:
        return 0.0

    return 1/((df)**(1/tau))-1


def df_to_rate(df:float, t_1:dt.date, t_2:dt.date) -> float:
    """
    Converts the discount factor P(t,T) to continuously compounded spot interest rate R(t)
    """
    tau = Actual365.year_fraction(t_1, t_2)
    if tau == 0.0:
        return 0.0

    return -(np.log(df))/tau


def zero_to_df(y:float, t_1:dt.date, t_2:dt.date) -> float:
    """
    Converts the annually compounded spot interest rate Y(t,T) to a discount factor P(t,T).
    """
    tau = Actual365.year_fraction(t_1, t_2)
    if (tau == 0.0):
        return 1.0

    return 1/((1 + y)**tau)


def df_to_forward(df1, df2, t, s) -> float:
    """Extracts the forward from a pair of discount factors"""
    tau = Actual365.year_fraction(t, s)
    return (1/tau) * (df1/df2 - 1)


def is_leap_year(year:int) -> bool:
    """Test if the given year is a leap year"""
    return ((year % 4 == 0) and (not(year % 100 == 0))) or (year % 400 == 0);


def length_of_year(yy:int) -> int:
    """Returns the number of days in a year"""
    return 366 if is_leap_year(yy) else 365


def ensure_leap_year(d : dt.date) -> dt.date:
    """
    Returns the 29th of February if the current year is a leap year, else looks for
    the next near nearest 29th Feb.
    """
    if (is_leap_year(d.year)):
        return dt.date(d.year, 2, 29)
    elif (is_leap_year(d.year+1)):
        return dt.date(d.year + 1, 2, 29)
    elif (is_leap_year(d.year+2)):
        return dt.date(d.year + 2, 2, 29)
    elif (is_leap_year(d.year+3)):
        return dt.date(d.year + 3, 2, 29)
    else:
        return dt.date(d.year + 4, 2, 29)


def next_leap_day(d : dt.date) -> dt.date:
    """Returns the next leap date"""
    # Handle if already a leap day, move forward either 4 or 8 years.
    if d.month == 2 and d.day == 29:
        if is_leap_year(d.year):
            return ensure_leap_year(dt.date(d.year+4,d.month,d.day))

    # Handle if before February in a leap year.
    if d.month <= 2 and is_leap_year(d.year):
        return dt.date(d.year,2,29)

    # Handle any other date
    yy = (d.year // 4) * 4
    return ensure_leap_year(dt.date(yy + 4, 2, 29))


def get_length_of_month(d : dt.date) -> int:
    """Returns the number of days in a month"""
    _, num_days = calendar.monthrange(d.year, d.month)
    return num_days


def first_in_month(year : int, month : int, day_of_week : DayOfWeek):
    """Returns the first day_of_week in the month"""
    first_of_month = dt.date(year,month,1)
    result = first_of_month

    while result.weekday() != day_of_week:
        result = result + dt.timedelta(days=1)

    return result


def last_in_month(year : int, month : int, day_of_week : DayOfWeek):
    """Returns the last day_of_week in the given month"""
    first_of_month = dt.date(year, month, 1)
    num_days = get_length_of_month(first_of_month)
    end_of_month = dt.date(year,month,num_days)
    result = end_of_month

    while result.weekday() != day_of_week:
        result = result - dt.timedelta(days=1)

    return result


def easter(year:int) -> dt.date:
    """
    Butcher's algorithm to calculate the Easter day of any given year.
    Reference. https://en.wikipedia.org/wiki/Date_of_Easter
    """
    a = year % 19
    b = (year // 100)
    c = year % 100
    d = b // 4
    e = b % 4
    f = ((b + 8) // 25)
    g = (b - f + 1)
    h = (19 * a + b - d - g + 15) % 30
    i = (c // 4)
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = ((a + 11 * h + 22 * l) // 451)
    month = ((h + l - 7 * m + 114) // 31)
    dd = ((h + l - 7 * m + 114) % 31) + 1

    return dt.date(year,month,dd)


def bump_sun_to_mon(d : dt.date) -> dt.date:
    """Bumps to monday, if the given date falls on a sunday"""
    if d.weekday() == DayOfWeek.SUNDAY:
        return d + dt.timedelta(days=1)

    return d


def bump_to_mon(d : dt.date) -> dt.date:
    """Bumps to monday, if the given date falls on a weekend"""
    if d.weekday() == DayOfWeek.SATURDAY:
        return d + dt.timedelta(days = 2)
    elif d.weekday() == DayOfWeek.SUNDAY:
        return d + dt.timedelta(days = 1)
    else:
        return d


def bump_to_fri_or_mon(d : dt.date) -> dt.date:
    """Bumps saturday to friday and sunday to monday"""
    if d.weekday() == DayOfWeek.SATURDAY:
        return d - dt.timedelta(days = 1)

    if d.weekday() == DayOfWeek.SUNDAY:
        return d + dt.timedelta(days = 1)

    return d

def christmas_bumped_sat_or_sun(year:int) -> dt.date:
    """If Christmas falls on saturday or sunday, move to 27th December"""
    base = dt.date(year,12,25)
    if base.weekday() == DayOfWeek.SATURDAY or base.weekday() == DayOfWeek.SUNDAY:
        return dt.date(year,12,27)

    return base

def christmas_bumped_sun(year: int) -> dt.date:
    """If Christmas is on sunday, moved to Monday"""
    base = dt.date(year,12,25)
    if base.weekday() == DayOfWeek.SUNDAY:
        return dt.date(year,12,26)

    return base

def boxing_day_bumped_sun(year: int) -> dt.date:
    """Boxing day (if Christmas is sunday, boxing day moved from Monday to Tuesday)"""
    base = dt.date(year,12,26)
    if base.weekday() == DayOfWeek.MONDAY:
        return dt.date(year,12,27)

    return base

def boxing_day_bumped_sat_sun(year: int) -> dt.date:
    """If boxing day is on saturday(sunday), bumped to monday(tuesday)"""
    base = dt.date(year, 12, 26)
    if base.weekday() == DayOfWeek.SATURDAY or base.weekday() == DayOfWeek.SUNDAY:
        return dt.date(year,12,28)

    return base

def draw(x:Any, y:Any, xlabel: str, ylabel: str, title:str):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.plot(x,y,alpha=0.75,linewidth=0.80)
    plt.show()