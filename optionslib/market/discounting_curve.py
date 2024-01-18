import datetime
from datetime import date, timedelta
from enum import IntEnum, auto

import numpy as np
from optionslib.basics.interpolators import LinearInterpolator

from optionslib.basics import utils
from optionslib.basics.day_count_basis import Actual365


class DiscountingInterpolationMethod(IntEnum):
    LINEAR_ON_DISCOUNT_FACTORS = auto()
    LINEAR_ON_RATES = auto()
    LINEAR_ON_LOG_OF_RATES = auto()
    LINEAR_ON_LOG_OF_DISCOUNT_FACTORS = auto()
    NATURAL_CUBIC_SPLINE = auto()
    BESSEL_CUBIC_SPLINE = auto()
    FINANCIAL_CUBIC_SPLINE = auto()
    QUARTIC_SPLINE = auto()


## A curve object that stores discount factors.
#
# A `DiscountingCurve` object stores a vector of dates and discount factors.
# There is a need to value all instruments consistently within a single valuation
# framework. For this we need a risk-free discounting curve which will be a continuous
# curve (because this is the standard format for all option pricing formulae).
#
# We establish a few important results.
#
# Definition. (Risk-free asset). Consider an asset with the price process \f$(B_t:t \in [0,T])\f$
# which has the dynamics:
# $$dB(t) = r(t)B(t)dt$$
#
# where \f$r(t)\f$ is any adapted process. \f$B_t\f$ has no driving Wiener process (\f$dW_t\f$ term).
# Such an asset is said to be a risk-free asset. This corresponds to a bank account with (possibly stochastic
# short interest rate \f$r(t)\f$. Note, that the bank-account is *locally risk-free*, in the sense that,
# even if the short rate is a random process, the return \f$r(t)\f$ over an infinitesimal time-period
# \f$dt\f$ is risk-free (that is deterministic, given the information available at time \f$t\f$). However,
# the return of \f$B\f$ over a longer time period is typically stochastic.
#
# Using ODE cookbook methods, we can solve the above equation using separation of variables:
# $$B(t) = B(0) e^{\int_{0}^{t} r(s) ds}$$
#
# Definition. (Discounting process). The discounting process is defined as \f$D(t)=\frac{1}{B(t)}\f$. It is
# easy to see that the dynamics of \f$D(t)\f$ is:
# $$D(t) = -r(t)D(t)dt$$
#
# with solution
# $$D(0) = D(t)e^{-\int_{0}^{t} r(s) ds}$$
#
# Definition. (Stochastic Discount Factor). The (stochastic) discount factor between two time instants
# \f$t\f$ and \f$T\f$ is the amount at time \f$t\f$ equal to one unit of currency payable at time \f$T\f$
# and is given by:
# $$D(t,T) = \frac{B(t)}{B(T)} = e^{-\int_{t}^{T} r(s) ds}$$
#
# Definition. (Zero coupon bond). A \f$T\f$ maturity zero-coupon bond is a contract that guarantees its holder
# the payment of one unit of currency at time \f$T\f$, with no intermediate payments. The contract value at time
# \f$t < T\f$ is denoted by \f$P(t,T)\f$. Clearly, \f$P(T,T) = 1\f$ for all \f$T\f$.
#
# By the risk neutral pricing formula, the price \f$P(t,T)\f$ of this claim at time \f$t\f$ is given by:
#
# $$\frac{P(t,T)}{B(t)} = \mathbb{E}^{\mathbb{Q}}\left[\frac{1}{B(T)}|\mathcal{F}_t\right]$$
#
# In other words,
#  $$P(t,T) = \mathbb{E}^{\mathbb{Q}}\left[\frac{B(t)}{B(T)}|\mathcal{F}_t\right]= \mathbb{E}^{\mathbb{Q}}\left[D(t,T)|\mathcal{F}_t\right]$$
#
# What is the relationship between the stochastic discount factor \f$D(t,T)\f$ and the zero-coupon bond price \f$P(t,T)\f$
# for each pair \f$(t,T)\f$? If the rates \f$r\f$ are deterministic, then \f$D\f$ is deterministic as well and
# \f$D(t,T) = P(t,T)\f$. However, if the rates are stochastic, \f$D(t,T)\f$ is a random quantity at time \f$t\f$
# depending on the future evolution of the rates \f$r\f$ between \f$t\f$ and \f$T\f$.
#
# *Remark.* It is common to refer to the ZCB price \f$P(t,T)\f$ as just the discount factor.
#
#  Definition (Continuously compounded spot interest rate). The continuously compounded spot interest rate prevailing
# at time \f$t\f$ for the maturity \f$T\f$ is denoted by \f$R(t,T)\f$ and is the constant rate at which an investment
# of \f$P(t,T)\f$ units of currency at time \f$t\f$ accrues continuous to yield a unit amount of currency at
# maturity \f$T\f$. In formulas:
# $$ P(t,T)\exp{(R(t,T)\tau(t,T))} = 1$$
#
# or
# $$ R(t,T) = -\frac{\ln P(t,T)}{\tau(t,T)}$$
#
# Definition (Annually compounded spot interest rate). The annually compounded spot interest rate prevailing at
# time \f$t\f$ for the maturity \f$T\f$ is denoted by \f$Y(t,T)\f$ and is the constant rate at which
# investment has to be made to produce an amount of one unit of currency at maturity starting from
# \f$P(t,T)\f$ units of currency at time \f$t\f$, when reinvesting the obtained amounts once a year. In formulas,
# $$P(t,T)[1 + Y(t,T)]^{\tau(t,T)} = 1$$
#
# Solving for \f$Y(t,T)\f$, we have:
#
# $$Y(t,T) := \frac{1}{[P(t,T)]^{\frac{1}{\tau(t,T)}}} - 1$$
#
# Thus, zero-coupon bond prices can be expressed in terms of annually compounded rates as:
#
# $$P(t,T) = \frac{1}{[1+Y(t,T)]^{\tau(t,T)}}$$
#
# Definition (Simply-compounded spot interest rate). The simply compounded spot interest rate prevailing at
# time \f$t\f$ for maturity \f$T\f$ is denoted by \f$L(t,T)\f$ and is the constant rate at which
# an investment has to be made to produce one unit of currency at maturity, starting from \f$P(t,T)\f$
# units of currency at time \f$t\f$, when accruing occurs proportionally to the investment time.
# In formulas:
# $$P(t,T)[1 + L(t,T) \times \tau(t,T)]=1$$
#
# Solving for \f$L(t,T)\f$, we have:
# $$L(t,T) := \frac{1 - P(t,T)}{\tau(t,T)P(t,T)}$$
#
# Reference : http://www.deriscope.com/docs/Hagan_West_curves_AMF.pdf
#


class DiscountingCurve:
    def __init__(
        self,
        dates: np.ndarray,
        discountFactors: np.ndarray,
        discInterpMethod: DiscountingInterpolationMethod = DiscountingInterpolationMethod.FINANCIAL_CUBIC_SPLINE,
    ):
        self.dates = dates
        self.dfs = discountFactors
        self.DiscountingInterpolationMethod = discInterpMethod

    def dateSetForPlot(self):
        anchorDate = self.dates[0]
        terminalDate = anchorDate + datetime.timedelta(days=365 * 5)
        nPoints = (terminalDate - anchorDate).days + 1
        return (
            anchorDate,
            [anchorDate + timedelta(days=i) for i in range(nPoints)],
            nPoints,
        )

    def plotDFs(self):
        startDate, dates, n = self.dateSetForPlot()
        discountFactors = [self.discountFactor(startDate, dates[i]) for i in range(n)]
        Utils.draw(
            x=dates,
            y=discountFactors,
            xlabel=r"Time $t$",
            ylabel=r"Discount factor $P(0,t)$",
            title="Discount factor curve",
        )

    def plotRates(self):
        startDate, dates, n = self.dateSetForPlot()
        rates = [self.rate(startDate, dates[i]) for i in range(n)]
        Utils.draw(
            x=dates,
            y=rates,
            xlabel=r"Time $t$",
            ylabel=r"Rate $R(0,t)$",
            title="Rates curve",
        )

    def plotZeroCouponCurve(self):
        startDate, dates, n = self.dateSetForPlot()
        zeroCouponRates = [self.zero(startDate, dates[i]) for i in range(n)]
        Utils.draw(
            x=dates,
            y=zeroCouponRates,
            xlabel=r"Time $t$",
            ylabel=r"Zero coupon $Y(0,t)$",
            title="Zero Coupon curve",
        )

    def plotForwardCurve(self):
        startDate, dates, n = self.dateSetForPlot()
        forwardRates = [
            self.forward(startDate, dates[i], dates[i] + datetime.timedelta(days=365))
            for i in range(n)
        ]
        Utils.draw(
            x=dates,
            y=forwardRates,
            xlabel=r"Time $t$",
            ylabel=r"Forward $F(0,T,S)$",
            title="1y Forward curve",
        )

    ## Returns the discount factor P(t,T) between times t and T.
    def discountFactor(self, t: datetime.date, T: datetime.date):
        anchorDate = self.dates[0]
        result = 0.0
        interpolator = None

        if (
            self.DiscountingInterpolationMethod
            == DiscountingInterpolationMethod.LINEAR_ON_DISCOUNT_FACTORS
        ):
            interpolator = LinearInterpolator(self.dates, self.dfs)

            # The discount factor P(0,t)
            df_t = interpolator(t)

            # The discount factor P(0,T)
            df_T = interpolator(T)

            # We know that, P(0,T) = P(0,t) x P(t,T)
            result = (df_T) / (df_t)

        if (
            self.DiscountingInterpolationMethod
            == DiscountingInterpolationMethod.LINEAR_ON_RATES
        ):
            rates = np.ndarray([self.rate(anchorDate, t) for i in len(self.dfs)])

            interpolator = LinearInterpolator(self.dates, rates)

            # The rate R(0,t)
            r_t = interpolator(t)

            # The rate R(0,T)
            r_T = interpolator(T)

            # We know that e^(R(t,T)tau(t,T)) = e^(R(0,T)tau(0,T))/e^(R(0,t)tau(0,t))
            tau_t = Actual365.year_fraction(anchorDate, t)
            tau_T = Actual365.year_fraction(anchorDate, T)

            compoundFactor = np.exp(r_T * tau_T) / np.exp(r_t * tau_t)
            result = 1 / compoundFactor

        if (
            self.DiscountingInterpolationMethod
            == DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_RATES
        ):
            logRates = np.ndarray(
                [np.log(self.rate(anchorDate, t)) for i in len(self.dfs)]
            )

            interpolator = LinearInterpolator(self.dates, logRates)

            # log R(0,t)
            logR_t = interpolator(t)

            # log R(0,T)
            logR_T = interpolator(T)

            R_t = np.exp(logR_t)
            R_T = np.exp(logR_T)

            tau_t = Actual365.year_fraction(anchorDate, t)
            tau_T = Actual365.year_fraction(anchorDate, T)

            compoundFactor = np.exp(R_t * tau_T) / np.exp(R_T * tau_t)
            result = 1 / compoundFactor

        if (
            self.DiscountingInterpolationMethod
            == DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_DISCOUNT_FACTORS
        ):
            logDfs = np.log(self.dfs)

            interpolator = LinearInterpolator(self.dates, logDfs)

            # log P(0,t)
            logP_t = interpolator(t)

            # log P(0,T)
            logP_T = interpolator(T)

            P_t = np.exp(logP_t)
            P_T = np.exp(logP_T)
            return P_T / P_t

    ## Returns the annual compounded spot interest rate(zero) Y(t,T) between times t and T
    def zero(self, t: date, T: date):
        return Utils.df_to_zero(self.discountFactor(t, T), t, T)

    ## Returns the continuous compounded spot rate R(t,T) between times t and T
    def rate(self, t: date, T: date):
        return Utils.df_to_rate(self.discountFactor(t, T), t, T)

    ## Returns the simply compounded forward rate F(t;T,S) between times T and S, as observed on t
    def forward(self, t: date, T: date, S: date):
        return Utils.df_to_forward(
            self.discountFactor(t, T), self.discountFactor(t, S), T, S
        )


if __name__ == "__main__":
    dates = [
        datetime.date(2023, 1, 1),
        datetime.date(2024, 1, 1),
        datetime.date(2025, 1, 1),
        datetime.date(2026, 1, 1),
        datetime.date(2027, 1, 1),
        datetime.date(2028, 1, 1),
    ]

    dfs = [
        1.00,
        (1.05) ** (-1),
        (1.05) ** (-2),
        (1.05) ** (-3),
        (1.05) ** (-4),
        (1.05) ** (-5),
    ]

    discountingCurve = DiscountingCurve(
        dates, dfs, DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_DISCOUNT_FACTORS
    )
    today = datetime.date(2023, 1, 1)
    df = discountingCurve.discountFactor(today, datetime.date(2024, 6, 1))
    print(f"DF = {df}")
    discountingCurve.plotZeroCouponCurve()
