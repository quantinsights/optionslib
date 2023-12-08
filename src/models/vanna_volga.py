"""
This module implements the Vanna-Volga approximation for constructing a smile.
"""
from typing import List, Union
import datetime as dt
import numpy as np
from scipy.stats import norm

from src.basics.DayCountBasis import Actual365
from src.basics.Enums import FxOptionsMarketQuoteType
from src.market.EuropeanVanillaFxOptionQuote import EuropeanVanillaFxOptionQuote
from src.market.discounting_curve import DiscountingCurve

NumericType = Union[int, float, np.number]

class VannaVolga:
    """
    This is an abstraction of the Vanna-Volga approximation.
    """

    def __init__(
            self,
            fx_option_market_quotes : List[EuropeanVanillaFxOptionQuote],
            s_t : float,
            foreign_ccy_discounting_curve : DiscountingCurve,
            domestic_ccy_discounting_curve : DiscountingCurve
    ):
        self.validate_type(
            fx_option_market_quotes,
            "fx_option_market_quotes",
            List[EuropeanVanillaFxOptionQuote]
        )

        self.validate_type(
            s_t,
            "s_t",
            NumericType
        )

        self.validate_type(
            foreign_ccy_discounting_curve,
            "foreign_ccy_discounting_curve",
            DiscountingCurve
        )

        self.validate_type(
            domestic_ccy_discounting_curve,
            "domestic_ccy_discounting_curve",
            DiscountingCurve
        )
        
        self.__fx_option_market_quotes = fx_option_market_quotes
        self.__s_t = s_t
        self.__foreign_discounting_curve = foreign_ccy_discounting_curve
        self.__domestic_discounting_curve = domestic_ccy_discounting_curve

        self.__valuation_date = fx_option_market_quotes[0].asOfDate \
            if len(fx_option_market_quotes) > 0 else dt.date.today()

        self.__risk_rev = {}
        self.__stdl = {}
        self.__vwb = {}

        for quote in enumerate(fx_option_market_quotes):
            if (quote.quoteType ==
                    FxOptionsMarketQuoteType.ATM_STRADDLE):
                self.__stdl[quote.expiryDate] = quote.vol
            elif (quote.quoteType ==
                  FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_RISK_REVERSAL):
                self.__risk_rev[quote.expiryDate] = quote.vol
            elif (quote.quoteType ==
                  FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY):
                self.__vwb[quote.expiryDate] = quote.vol

        self.__exp_dates = np.array(self.__stdl.keys())
        self.__time_to_expiries = np.array([Actual365(self.__valuation_date, expDate)
                                            for expDate in self.__exp_dates])

        # Calculate the ATM, 25-Delta call and 25-Delta Put (pivot option) quotes
        sigma_atm = np.array(self.__stdl.values())
        sigma_25d_rr = np.array(self.__risk_rev.values())
        sigma_25d_fly = np.array(self.__vwb.values())

        self.__sigma_atm = sigma_atm
        self.__sigma_25d_call = (sigma_25d_fly + sigma_atm) + 0.50 * sigma_25d_rr
        self.__sigma_25d_put = (sigma_25d_fly + sigma_atm) - 0.50 * sigma_25d_rr

        # Calculate the ATM, 25-Delta call and 25-Delta put strikes
        # for each expiry.
        self.__fwd_t = np.array([self.forward(self.__valuation_date, exp_date)
                                 for exp_date in self.__exp_dates])
        self.__k_atm = self.__fwd_t * np.exp((self.__sigma_atm ** 2) / 2 * self.__time_to_expiries)
        self.__compound_factors = (
            np.array([1 / self.__domestic_discounting_curve.discountFactor(
                self.__valuation_date,
                exp_date
        )
                      for exp_date in self.__exp_dates]))
        self.__alpha = np.array([-norm.ppf(0.25 * compound_factor)
                                 for compound_factor in self.__compound_factors])
        self.__k_25d_call = self.__fwd_t * np.exp(
            self.__alpha * self.__sigma_25d_call * np.sqrt(self.__time_to_expiries) +
            0.50 * (self.__sigma_25d_call ** 2) * self.__time_to_expiries
        )
        self.__k_25d_put = self.__fwd_t * np.exp(
            -self.__alpha * self.__sigma_25d_put * np.sqrt(self.__time_to_expiries) +
            0.50 * (self.__sigma_25d_put ** 2) * self.__time_to_expiries
        )

        self.__data_by_expiry = {}
        i = 0
        for exp_date in enumerate(self.__exp_dates):
            self.__data_by_expiry[exp_date] = (
                self.__time_to_expiries[i],
                self.__sigma_atm[i],
                self.__sigma_25d_call[i],
                self.__sigma_25d_put[i],
                self.__fwd_t[i],
                self.__k_atm[i],
                self.__k_25d_call[i],
                self.__k_25d_put[i]
            )
            i += 1

    def validate_type(self,value,var_name, expected_type):
        if not(isinstance(value,expected_type)):
            raise ValueError(f"{var_name} must be of type {expected_type}!")

    def validate_nonnegative(self, value, var_name):
        if value < 0:
            raise ValueError(f"{var_name} must be >= 0")

    def forward(self, t_1:dt.date, t_2:dt.date) -> float:
        """
        Returns the foward F(t_1,t_2)
        """
        foreign_df = self.__foreign_discounting_curve.discountFactor(t_1, t_2)
        domestic_df = self.__domestic_discounting_curve.discountFactor(t_1, t_2)
        fwd_points = foreign_df / domestic_df
        fwd = fwd_points * self.__s_t
        return fwd

    def first_order_approximation(self, k:float, t_exp:dt.date) -> float:
        """
        The first order smile approximation sigma(K,T)
        """
        if t_exp in self.__data_by_expiry:
            tau, sigma_2, sigma_3, sigma_1, fwd_t_exp, k_2, k_3, k_1 = self.__data_by_expiry[t_exp]
            y_1 = (np.log(k_2 / k) * np.log(k_3 / k)) / (np.log(k_3 / k_1) * np.log(k_2 / k_1))
            y_2 = (np.log(k / k_1) * np.log(k_3 / k)) / (np.log(k_2 / k_1) * np.log(k_3 / k_2))
            y_3 = (np.log(k / k_1) * np.log(k / k_2)) / (np.log(k_3 / k_1) * np.log(k_3 / k_2))
            return y_1 * sigma_1 + y_2 * sigma_2 + y_3 * sigma_3

        raise Exception(f"Market quotes for the expiry {dt.date.strftime(t_exp, '%Y-%m-%d')} "
                        f"were not supplied during VV calibration!")

    def second_order_approximation(self, k:float, t_exp:dt.date) -> float:
        """
        The second order smile approximation sigma(K,T)
        """
        if t_exp in self.__data_by_expiry:
            tau, sigma_2, sigma_3, sigma_1, fwd_t_exp, k_2, k_3, k_1 = self.__data_by_expiry[t_exp]
            xi1 = self.first_order_approximation(k, t_exp)
            d1_k = xi1 - sigma_2

            d_plus_k = self.d_plus(fwd_t_exp, k, sigma_2, tau)
            d_minus_k = self.d_minus(fwd_t_exp, k, sigma_2, tau)

            d_plus_k1 = self.d_plus(fwd_t_exp, k_1, sigma_2, tau)
            d_minus_k1 = self.d_minus(fwd_t_exp, k_1, sigma_2, tau)

            d_plus_k3 = self.d_plus(fwd_t_exp, k_3, sigma_2, tau)
            d_minus_k3 = self.d_minus(fwd_t_exp, k_3, sigma_2, tau)

            d2_k = ((d_plus_k1 * d_minus_k1 * (np.log(k_3 / k) * np.log(k_2 / k)) /
                     (np.log(k_3 / k_1) * np.log(k_2 / k_1)) *
                     (sigma_1 - sigma_2) ** 2 +
                     d_plus_k3 * d_minus_k3 * (np.log(k / k_1) * np.log(k / k_2)) /
                     (np.log(k_3 / k_1) * np.log(k_3 / k_2))) *
                    (sigma_3 - sigma_2) ** 2)

            return (sigma_2 + (-sigma_2 +
                               np.sqrt(sigma_2**2 -
                                       d_plus_k * d_minus_k * (2*sigma_2*d1_k + d2_k)))/
                    (d_plus_k * d_minus_k))

        raise Exception(f"Market quotes for the expiry {dt.date.strftime(t_exp, '%Y-%m-%d')} "
                        f"were not supplied during VV calibration!")

    def d_plus(self, fwd, k, tau, sigma):
        """
        Returns d+ in the Black-Scholes model
        """
        return (np.log(fwd / k) + tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))

    def d_minus(self, fwd, k, tau, sigma):
        """
        Returns d- in the Black-Scholes model
        """
        return (np.log(fwd / k) - tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))
