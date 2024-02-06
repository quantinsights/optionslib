"""Discounting Curve."""

import datetime as dt

import numpy as np
from attr import define, field

import optionslib.utils.visualisation
from optionslib.math.interpolation import LinearInterpolator
from optionslib.time.day_count_basis import Actual365
from optionslib.types.enums import DiscountingInterpolationMethod


def df_to_zero(discount_factor: float, t_1: dt.date, t_2: dt.date) -> float:
    """Converts the discount factor P(t,T) to the annually compounded spot interest rate
    Y(t,T)."""
    tau = Actual365.year_fraction(t_1, t_2)
    return 1 / discount_factor ** (1 / tau) - 1 if tau else 0


def df_to_rate(discount_factor: float, t_1: dt.date, t_2: dt.date) -> float:
    """Converts the discount factor P(t,T) to continuously compounded spot interest rate
    R(t)"""
    tau = Actual365.year_fraction(t_1, t_2)
    return -(np.log(discount_factor)) / tau if tau else 0


def rate_to_df(rate: float, t_1: dt.date, t_2: dt.date) -> float:
    """Converts the continuously compounded spot interest rate R(t) to a discount factor
    P(t,T)"""
    tau = Actual365.year_fraction(t_1, t_2)
    return np.exp(-rate * tau)


def zero_to_df(y: float, t_1: dt.date, t_2: dt.date) -> float:
    """Converts the annually compounded spot interest rate Y(t,T) to a discount factor
    P(t,T)."""
    tau = Actual365.year_fraction(t_1, t_2)
    return 1 / ((1 + y) ** tau) if tau else 1


def df_to_forward(discount_factor1, discount_factor2, t_1, t_2) -> float:
    """Extracts the forward from a pair of discount factors."""
    tau = Actual365.year_fraction(t_1, t_2)
    return (1 / tau) * (discount_factor1 / discount_factor2 - 1) if tau else 0


@define
class DiscountingCurve:
    """Class to represent a discount curve object."""

    dates: np.ndarray[dt.date]
    discount_factors: np.ndarray[float]
    interpolation_method: DiscountingInterpolationMethod = field(
        default=DiscountingInterpolationMethod.FINANCIAL_CUBIC_SPLINE
    )

    def date_set_for_plot(self):
        """Sets up the dates for plotting."""
        anchor_date = self.dates[0]
        terminal_date = anchor_date + dt.timedelta(days=365 * 5)
        n_points = (terminal_date - anchor_date).days + 1
        return (
            anchor_date,
            [anchor_date + dt.timedelta(days=i) for i in range(n_points)],
            n_points,
        )

    def plot_discount_factors(self):
        """Plot discount factors."""
        start_date, dates, n = self.date_set_for_plot()
        discount_factors = [
            self.discount_factor(start_date, dates[i]) for i in range(n)
        ]
        optionslib.utils.visualisation.draw(
            x=dates,
            y=discount_factors,
            xlabel=r"Time $t$",
            ylabel=r"Discount factor $P(0,t)$",
            title="Discount factor curve",
        )

    def plot_rates(self):
        """Plots the rates."""
        start_date, dates, n = self.date_set_for_plot()
        rates = [self.rate(start_date, dates[i]) for i in range(n)]
        optionslib.utils.visualisation.draw(
            x=dates,
            y=rates,
            xlabel=r"Time $t$",
            ylabel=r"Rate $R(0,t)$",
            title="Rates curve",
        )

    def plot_zero_coupon_curve(self):
        """Plots the zero coupon curve."""
        start_date, dates, n = self.date_set_for_plot()
        zero_coupon_rates = [self.zero(start_date, dates[i]) for i in range(n)]
        optionslib.utils.visualisation.draw(
            x=dates,
            y=zero_coupon_rates,
            xlabel=r"Time $t$",
            ylabel=r"Zero coupon $Y(0,t)$",
            title="Zero Coupon curve",
        )

    def plot_forward_curve(self):
        """Plot the forward rates."""
        start_date, dates, n = self.date_set_for_plot()
        forward_rates = [
            self.forward(start_date, dates[i], dates[i] + dt.timedelta(days=365))
            for i in range(n)
        ]
        optionslib.utils.visualisation.draw(
            x=dates,
            y=forward_rates,
            xlabel=r"Time $t$",
            ylabel=r"Forward $F(0,T,S)$",
            title="1y Forward curve",
        )

    def discount_factor(self, t_1: dt.datetime.date, t_2: dt.datetime.date) -> float:
        """Returns the discount factor P(t,T) between times t and T."""
        anchor_date = self.dates[0]

        match self.interpolation_method:
            case DiscountingInterpolationMethod.LINEAR_ON_DISCOUNT_FACTORS:
                interpolator = LinearInterpolator(
                    self.dates, self.discount_factors, extrapolate=True
                )
                # P(0,T) = P(0,t) x P(t,T)
                return interpolator(t_2) / interpolator(t_1)
            case DiscountingInterpolationMethod.LINEAR_ON_RATES:
                rates = np.ndarray(
                    [self.rate(anchor_date, t_1) for i in len(self.discount_factors)]
                )
                interpolator = LinearInterpolator(self.dates, rates, extrapolate=True)

                def compound_from_anchor(t):
                    r_t = interpolator(t)
                    tau_t = Actual365.year_fraction(anchor_date, t)
                    return np.exp(r_t * tau_t)

                # e^(R(t,T)tau(t,T)) = e^(R(0,T)tau(0,T))/e^(R(0,t)tau(0,t))
                return compound_from_anchor(t_1) / compound_from_anchor(t_2)
            case DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_RATES:
                log_rates = np.ndarray(
                    [np.log(self.rate(anchor_date, t_)) for t_ in self.dates]
                )
                interpolator = LinearInterpolator(
                    self.dates, log_rates, extrapolate=True
                )

                def compound_from_anchor_log(t):
                    log_r_t = interpolator(t)
                    r_t = np.exp(log_r_t)
                    tau_t = Actual365.year_fraction(anchor_date, t)
                    return np.exp(r_t * tau_t)

                return compound_from_anchor_log(t_1) / compound_from_anchor_log(t_2)
            case DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_DISCOUNT_FACTORS:
                log_dfs = np.log(self.discount_factors)
                interpolator = LinearInterpolator(self.dates, log_dfs, extrapolate=True)

                log_p_t_1 = interpolator(t_1)
                log_p_t_2 = interpolator(t_2)
                p_t_1 = np.exp(log_p_t_1)
                p_t_2 = np.exp(log_p_t_2)
                return p_t_2 / p_t_1
            case _:
                raise NotImplementedError("Not implemented yet")

    def zero(self, t_1: dt.datetime.date, t_2: dt.datetime.date) -> float:
        """Returns the annual compounded spot interest rate(zero) Y(t,T) between times t
        and T."""
        return df_to_zero(
            self.discount_factor(t_1, t_2),
            t_1,
            t_2,
        )

    def rate(self, t_1: dt.datetime.date, t_2: dt.datetime.date) -> float:
        """Returns the continuous compounded spot rate R(t,T) between times t and T."""
        return df_to_rate(
            self.discount_factor(t_1, t_2),
            t_1,
            t_2,
        )

    def forward(self, as_of: dt.date, t_1: dt.date, t_2: dt.date) -> float:
        """Returns the simply compounded forward rate F(t;T,S) between times T and S, as
        observed on t."""
        return df_to_forward(
            self.discount_factor(as_of, t_1),
            self.discount_factor(as_of, t_2),
            t_1,
            t_2,
        )

    def add_spread(self, spread: float):
        """Adds a fixed spread adjustment to the discounting rates"""
        curr_rates = [
            df_to_rate(self.discount_factors[i], self.dates[0], self.dates[i])
            for i in range(len(self.dates))
        ]

        rates_plus_spd = [curr_rates[i] + spread for i in range(len(self.dates))]

        self.discount_factors = [
            rate_to_df(rates_plus_spd[i], self.dates[0], self.dates[i])
            for i in range(len(self.dates))
        ]

        return self
