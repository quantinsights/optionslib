"""
This module implements the Vanna-Volga approximation for constructing a smile.
"""
from typing import Dict, List
from datetime import date
import numpy as np
from scipy.stats import norm

from src.basics.DayCountBasis import Actual365
from src.basics.Enums import FxOptionsMarketQuoteType
from src.market.EuropeanVanillaFxOptionQuote import EuropeanVanillaFxOptionQuote
from src.market.DiscountingCurve import DiscountingCurve



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
        self.fx_option_market_quotes = fx_option_market_quotes
        self.s_t = s_t
        self.foreign_discounting_curve = foreign_ccy_discounting_curve
        self.domestic_discounting_curve = domestic_ccy_discounting_curve

        self.valuation_date = fx_option_market_quotes[0].asOfDate \
            if len(fx_option_market_quotes) > 0 else date.today()

        self.risk_rev = {}
        self.stdl = {}
        self.vwb = {}

        for quote in enumerate(fx_option_market_quotes):
            if (quote.quoteType ==
                    FxOptionsMarketQuoteType.ATM_STRADDLE):
                self.stdl[quote.expiryDate] = quote.vol
            elif (quote.quoteType ==
                  FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_RISK_REVERSAL):
                self.risk_rev[quote.expiryDate] = quote.vol
            elif (quote.quoteType ==
                  FxOptionsMarketQuoteType.TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY):
                self.vwb[quote.expiryDate] = quote.vol

        self.exp_dates = np.array(self.stdl.keys())
        self.time_to_expiries = np.array([Actual365(self.valuation_date, expDate)
                                          for expDate in self.exp_dates])

        # Calculate the ATM, 25-Delta call and 25-Delta Put (pivot option) quotes
        sigma_atm = np.array(self.stdl.values())
        sigma_25d_rr = np.array(self.risk_rev.values())
        sigma_25d_fly = np.array(self.vwb.values())

        self.sigma_atm = sigma_atm
        self.sigma_25d_call = (sigma_25d_fly + sigma_atm) + 0.50 * sigma_25d_rr
        self.sigma_25d_put = (sigma_25d_fly + sigma_atm) - 0.50 * sigma_25d_rr

        # Calculate the ATM, 25-Delta call and 25-Delta put strikes
        # for each expiry.
        self.fwd_t = np.array([self.forward(self.valuation_date, exp_date)
                               for exp_date in self.exp_dates])
        self.k_atm = self.fwd_t * np.exp((self.sigma_atm ** 2) / 2 * self.time_to_expiries)
        self.compound_factors = (
            np.array([1 / self.domestic_discounting_curve.discountFactor(
                self.valuation_date,
                exp_date
        )
                                          for exp_date in self.exp_dates]))
        self.alpha = np.array([-norm.ppf(0.25*compound_factor)
                               for compound_factor in self.compound_factors])
        self.k_25d_call = self.fwd_t * np.exp(
            self.alpha * self.sigma_25d_call * np.sqrt(self.time_to_expiries) +
            0.50 * (self.sigma_25d_call ** 2) * self.time_to_expiries
        )
        self.k_25d_put = self.fwd_t * np.exp(
            -self.alpha * self.sigma_25d_put * np.sqrt(self.time_to_expiries) +
            0.50 * (self.sigma_25d_put ** 2) * self.time_to_expiries
        )

        self.data_by_expiry = {}
        i = 0
        for exp_date in enumerate(self.exp_dates):
            self.data_by_expiry[exp_date] = (
                self.time_to_expiries[i],
                self.sigma_atm[i],
                self.sigma_25d_call[i],
                self.sigma_25d_put[i],
                self.fwd_t[i],
                self.k_atm[i],
                self.k_25d_call[i],
                self.k_25d_put[i]
            )
            i += 1

    def forward(self, t_1:date, t_2:date):
        """
        Returns the foward \f$F(t_1,t_2)\f$
        """
        foreign_df = self.foreign_discounting_curve.discountFactor(t_1, t_2)
        domestic_df = self.domestic_discounting_curve.discountFactor(t_1, t_2)
        fwd_points = foreign_df / domestic_df
        fwd = fwd_points * self.s_t
        return fwd

    def first_order_approximation(self, k:float, t_exp:date):
        """
        The first order smile approximation \f$\sigma(K,T)\f$
        """
        if t_exp in self.data_by_expiry:
            tau, sigma_2, sigma_3, sigma_1, fwd_t_exp, k_2, k_3, k_1 = self.data_by_expiry[t_exp]
            y_1 = (np.log(k_2 / k) * np.log(k_3 / k)) / (np.log(k_3 / k_1) * np.log(k_2 / k_1))
            y_2 = (np.log(k / k_1) * np.log(k_3 / k)) / (np.log(k_2 / k_1) * np.log(k_3 / k_2))
            y_3 = (np.log(k / k_1) * np.log(k / k_2)) / (np.log(k_3 / k_1) * np.log(k_3 / k_2))
            return y_1 * sigma_1 + y_2 * sigma_2 + y_3 * sigma_3

        raise Exception(f"Market quotes for the expiry {date.strftime(t_exp, '%Y-%m-%d')} "
                        f"were not supplied during VV calibration!")

    def second_order_approximation(self, k:float, t_exp:date):
        """
        The second order smile approximation \f$\sigma(K,T)\f$
        """
        if t_exp in self.data_by_expiry.keys():
            tau, sigma_2, sigma_3, sigma_1, fwd_t_exp, k_2, k_3, k_1 = self.data_by_expiry[t_exp]
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

        raise Exception(f"Market quotes for the expiry {date.strftime(t_exp, '%Y-%m-%d')} "
                        f"were not supplied during VV calibration!")

    def d_plus(self, fwd, k, tau, sigma):
        """
        Returns \f$d_{+}\f$ in the Black-Scholes model
        """
        return (np.log(fwd / k) + tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))

    def d_minus(self, fwd, k, tau, sigma):
        """
        Returns \f$d_{-}\f$ in the Black-Scholes model
        """
        return (np.log(fwd / k) - tau * (sigma ** 2) / 2) / (sigma * np.sqrt(tau))
