"""This module implements the Vanna-Volga approximation for constructing a
smile.

Reference.
https://quantophile.github.io/mathsummaries/post/2023/11/26/implementing-vanna-volga/
"""

import datetime as dt
from typing import Union

import attrs.validators
import numpy as np
from attrs import define, field
from scipy.stats import norm

from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.products.european_vanilla_fx_option import EuropeanVanillaFxOptionQuote
from optionslib.time.day_count_basis import Actual365
from optionslib.types.enums import FxOptionsMarketQuote
from optionslib.types.var_types import NumericType


@define
class VannaVolga:
    """This is an abstraction of the Vanna-Volga approximation."""

    fx_option_market_quotes: list[EuropeanVanillaFxOptionQuote] = field(
        validator=attrs.validators.instance_of(list[EuropeanVanillaFxOptionQuote])
    )
    spot: float = field(
        validator=attrs.validators.and_(
            attrs.validators.instance_of(NumericType), attrs.validators.ge(0)
        )
    )
    foreign_ccy_discounting_curve: DiscountingCurve = field(
        validator=attrs.validators.instance_of(DiscountingCurve)
    )
    domestic_ccy_discounting_curve: DiscountingCurve = field(
        validator=attrs.validators.instance_of(DiscountingCurve)
    )

    # internal
    __risk_rev: dict[dt.date, float] = field(init=False)
    __stdl: dict[dt.date, float] = field(init=False)
    __vwb: dict[dt.date, float] = field(init=False)

    @property
    def valuation_date(self) -> dt.date:
        """Get the valuation date."""
        if len(self.fx_option_market_quotes) == 0:
            return dt.date.today()
        return self.fx_option_market_quotes[0].as_of_date

    @property
    def exp_dates(self):
        """Return the array of expiration dates."""
        return np.array(self.__stdl.keys())

    @property
    def time_to_expiries(self):
        """Return the array of time to expiry."""
        return [
            Actual365.year_fraction(self.valuation_date, exp_date)
            for exp_date in self.exp_dates
        ]

    def unpack_option_quotes(self):
        """
        This routine reads from a sequential list of market quotes and divides them into
        3 buckets - RR, STDL and FLY.

        The idea is, the most liquid quoted instruments in the FX options market are
        risk-reversals, straddles and butterflies.

        """
        for quote in self.fx_option_market_quotes:
            match quote.quote_type:
                case FxOptionsMarketQuote.ATM_STRADDLE:
                    target_dict = self.__stdl
                case FxOptionsMarketQuote.TWENTY_FIVE_DELTA_RISK_REVERSAL:
                    target_dict = self.__risk_rev
                case FxOptionsMarketQuote.TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY:
                    target_dict = self.__vwb
                case _:
                    raise ValueError(f"Unknown quote type {quote.quote_type}.")
            target_dict[quote.expiry_date] = quote.vol

        if not self.__check_option_quotes_integrity():
            raise ValueError(
                "STDL, RR and FLY quotes must be present for each maturity!"
            )

    def __check_option_quotes_integrity(self):
        """Check the integrity of market options quote data."""
        return all(
            (exp in self.__risk_rev) and (exp in self.__stdl) and (exp in self.__vwb)
            for exp in self.exp_dates
        )

    def sigma_atm(self, t: dt.date) -> float:
        """Returns the STDL vol quote."""
        return self.__stdl[t]

    def sigma_25d_rr(self, t: dt.date) -> float:
        """Returns the 25-delta risk reversal vol quote."""
        return self.__risk_rev[t]

    def sigma_25d_fly(self, t: dt.date) -> float:
        """Returns the 25-delta butterfly vol quotes."""
        return self.__vwb[t]

    def sigma_25d_call(self, t: dt.date) -> float:
        """Compute the 25-delta call volatility."""
        return (self.sigma_25d_fly(t) + self.sigma_atm(t)) + 0.50 * self.sigma_25d_rr(t)

    def sigma_25d_put(self, t: dt.date) -> float:
        """Compute the 25-delta put volatility."""
        return (self.sigma_25d_fly(t) + self.sigma_atm(t)) - 0.50 * self.sigma_25d_rr(t)

    def alpha(self, exp_date) -> float:
        """Computes the alpha given a expiration date."""
        compound_factor = 1 / self.domestic_ccy_discounting_curve.discount_factor(
            self.valuation_date, exp_date
        )
        return -norm.ppf(0.25 * compound_factor)

    def k_atm_call(self, exp_date) -> float:
        """Compute the ATM strike for a given smile(with certain expiration
        date)"""
        fwd = self.forward(self.valuation_date, exp_date)
        time_to_expiry = Actual365.year_fraction(self.valuation_date, exp_date)
        return fwd * np.exp((self.sigma_atm(exp_date) ** 2) / 2 * time_to_expiry)

    def k_25d_call(self, exp_date) -> float:
        """Compute the 25-delta call strike for a given smile(with certain
        expiration date)"""
        fwd = self.forward(self.valuation_date, exp_date)
        time_to_expiry = Actual365.year_fraction(self.valuation_date, exp_date)

        return fwd * np.exp(
            self.alpha(exp_date)
            * self.sigma_25d_call(exp_date)
            * np.sqrt(time_to_expiry)
            + 0.50 * (self.sigma_25d_call(exp_date) ** 2) * time_to_expiry
        )

    def k_25d_put(self, exp_date) -> float:
        """Compute the 25-delta put strike for a given smile(with certain
        expiration date)"""
        fwd = self.forward(self.valuation_date, exp_date)
        time_to_expiry = Actual365.year_fraction(self.valuation_date, exp_date)

        return fwd * np.exp(
            self.alpha(exp_date)
            * self.sigma_25d_put(exp_date)
            * np.sqrt(time_to_expiry)
            + 0.50 * (self.sigma_25d_put(exp_date) ** 2) * time_to_expiry
        )

    def forward(self, t_1: dt.date, t_2: dt.date) -> float:
        """Returns the foward F(t_1,t_2) between t_1 and t_2."""
        foreign_df = self.foreign_ccy_discounting_curve.discount_factor(t_1, t_2)
        domestic_df = self.domestic_ccy_discounting_curve.discount_factor(t_1, t_2)
        fwd_points = foreign_df / domestic_df
        fwd = fwd_points * self.spot
        return fwd

    def y_1(self, k_1, k_2, k_3, k):
        """Returns the term y_1 in first order linear approximation of VV-
        smile."""
        return (np.log(k_2 / k) * np.log(k_3 / k)) / (
            np.log(k_3 / k_1) * np.log(k_2 / k_1)
        )

    def y_2(self, k_1, k_2, k_3, k):
        """Returns the term y_2 in first order linear approximation of VV-
        smile."""
        return (np.log(k / k_1) * np.log(k_3 / k)) / (
            np.log(k_2 / k_1) * np.log(k_3 / k_2)
        )

    def y_3(self, k_1, k_2, k_3, k):
        """Returns the term y_3 in first order linear approximation of VV-
        smile."""
        return (np.log(k / k_1) * np.log(k / k_2)) / (
            np.log(k_3 / k_1) * np.log(k_3 / k_2)
        )

    def first_order_approximation(self, k: float, t_exp: dt.date) -> float:
        """The first order smile approximation sigma(K,T)"""
        if t_exp not in self.exp_dates:
            raise ValueError(
                f"Market quotes for the expiry {dt.date.strftime(t_exp, '%Y-%m-%d')} "
                f"were not supplied during VV calibration!"
            )

        sigma_1 = self.sigma_25d_put(t_exp)
        sigma_2 = self.sigma_atm(t_exp)
        sigma_3 = self.sigma_25d_call(t_exp)

        k_1 = self.k_25d_put(t_exp)
        k_2 = self.k_atm_call(t_exp)
        k_3 = self.k_25d_call(t_exp)

        y_1 = self.y_1(k_1, k_2, k_3, k)
        y_2 = self.y_2(k_1, k_2, k_3, k)
        y_3 = self.y_3(k_1, k_2, k_3, k)

        return y_1 * sigma_1 + y_2 * sigma_2 + y_3 * sigma_3

    def d2_k(
        self,
        t_exp: dt.date,
        k_1: float,
        k_2: float,
        k_3: float,
        k: float,
        sigma_1: float,
        sigma_2: float,
        sigma_3: float,
    ) -> float:
        """Returns the term D2(K) in the second-order approximation of VV-
        smile."""
        fwd = self.forward(self.valuation_date, t_exp)
        tau = Actual365.year_fraction(self.valuation_date, t_exp)
        return (
            self.d_plus(fwd, k_1, sigma_2, tau)
            * self.d_minus(fwd, k_1, sigma_2, tau)
            * (np.log(k_3 / k) * np.log(k_2 / k))
            / (np.log(k_3 / k_1) * np.log(k_2 / k_1))
            * (sigma_1 - sigma_2) ** 2
            + self.d_plus(fwd, k_3, sigma_2, tau)
            * self.d_minus(fwd, k_3, sigma_2, tau)
            * (np.log(k / k_1) * np.log(k / k_2))
            / (np.log(k_3 / k_1) * np.log(k_3 / k_2))
        ) * (sigma_3 - sigma_2) ** 2

    def second_order_approximation(self, k: float, t_exp: dt.date) -> float:
        """The second order smile approximation sigma(K,T)"""
        if t_exp in self.exp_dates:
            tau = Actual365.year_fraction(self.valuation_date, t_exp)

            sigma_1 = self.sigma_25d_put(t_exp)
            sigma_2 = self.sigma_atm(t_exp)
            sigma_3 = self.sigma_25d_call(t_exp)

            k_1 = self.k_25d_put(t_exp)
            k_2 = self.k_atm_call(t_exp)
            k_3 = self.k_25d_call(t_exp)

            fwd = self.forward(self.valuation_date, t_exp)

            xi1 = self.first_order_approximation(k, t_exp)

            d1_k = xi1 - sigma_2
            d_plus_minus_k = self.d_plus(fwd, k, sigma_2, tau) * self.d_minus(
                fwd, k, sigma_2, tau
            )
            d2_k = self.d2_k(t_exp, k_1, k_2, k_3, k, sigma_1, sigma_2, sigma_3)

            return (
                sigma_2
                + (
                    -sigma_2
                    + np.sqrt(sigma_2**2 - d_plus_minus_k * (2 * sigma_2 * d1_k + d2_k))
                )
                / d_plus_minus_k
            )

        raise ValueError(
            f"Market quotes for the expiry {dt.date.strftime(t_exp, '%Y-%m-%d')} "
            f"were not supplied during VV calibration!"
        )

    @staticmethod
    def d_plus(fwd, k, tau, sigma):
        """Returns d+ in the Black-Scholes model."""
        return (np.log(fwd / k) + tau * (sigma**2) / 2) / (sigma * np.sqrt(tau))

    @staticmethod
    def d_minus(fwd, k, tau, sigma):
        """Returns d- in the Black-Scholes model."""
        return (np.log(fwd / k) - tau * (sigma**2) / 2) / (sigma * np.sqrt(tau))


VolatilitySurfaceModel = Union[VannaVolga]
