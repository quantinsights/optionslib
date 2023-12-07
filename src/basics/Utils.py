from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from src.basics.DayCountBasis import Actual360, Actual365, ActualActual

## Converts the discount factor P(t,T) to the annually compounded spot interest rate Y(t,T).
def dfToZero(df: float, t:date, T:date):
    zeroRate = 0.0
    tau = Actual365.yearFraction(t,T)
    if (tau == 0.0):
        zeroRate = 0.0
    #elif (tau <= 1.0):
    #    zeroRate = (1 - df)/(df * tau)
    else:
        zeroRate = 1/((df)**(1/tau))-1
    return zeroRate

def dfToRate(df:float, t:date, T:date):
    tau = Actual365.yearFraction(t, T)
    if tau == 0.0:
        return 0.0
    else:
        return -(np.log(df))/tau

## Converts the annually compounded spot interest rate Y(t,T) to a discount factor P(t,T).
def ZeroToDf(y:float, t:date, T:date):
    df = 1.0
    tau = Actual365.yearFraction(t,T)
    if (tau == 0.0):
        df = 1.0
    #elif (tau<= 1.0):
    #    df = 1/(1 + y*tau)
    else:
        df = 1/((1 + y)**tau)

## Extracts the forward from a pair of discount factors
def dfToForward(df1,df2,T,S):
    tau = Actual365.yearFraction(T,S)
    return (1/tau) * (df1/df2 - 1)

## Test if the given year is a leap year
def isLeapYear(year:int):
    return ((year % 4 == 0) and (not(year % 100 == 0))) or (year % 400 == 0);

def lengthOfYear(yy:int):
    return 366 if isLeapYear(yy) else 365

def draw(x:Any, y:Any, xlabel: str, ylabel: str, title:str):
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.plot(x,y,alpha=0.75,linewidth=0.80)
    plt.show()