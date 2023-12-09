from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from src.basics.day_count_basis import Actual360, Actual365, ActualActual


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

def draw(x:Any, y:Any, xlabel: str, ylabel: str, title:str):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.plot(x,y,alpha=0.75,linewidth=0.80)
    plt.show()