"""Black calculator."""

from datetime import date

import numpy as np
from attr import define
from scipy.stats import norm

from optionslib.market.discounting_curve import DiscountingCurve, df_to_rate
from optionslib.market.european_vanilla_fx_option import EuropeanVanillaFxOption
from optionslib.time.day_count_basis import Actual365
from optionslib.types.enums import (
    FxOptionQuoteConvention,
    DeltaConvention,
)


@define
class BlackCalculator:
    """Standard Black formula calculator for European vanilla calls/puts."""

    valuation_date: date
    option_definition: EuropeanVanillaFxOption
    fx_spot: float
    foreign_discounting_curve: DiscountingCurve
    domestic_discounting_curve: DiscountingCurve
    sigma: float

    @property
    def year_fraction(self) -> float:
        """Calculates year fraction from valuation date to option maturity."""
        return Actual365.year_fraction(self.valuation_date, self.maturity)

    @property
    def d_plus(self):
        """Calculates d plus."""
        return (
            np.log(self.atm_forward / self.strike)
            + self.year_fraction * (self.sigma**2) / 2
        ) / (self.sigma * np.sqrt(self.year_fraction))

    @property
    def d_minus(self):
        """Calculates d minus."""
        return (
            np.log(self.atm_forward / self.strike)
            - self.year_fraction * (self.sigma**2) / 2
        ) / (self.sigma * np.sqrt(self.year_fraction))

    @property
    def omega(self):
        """Returns option direction."""
        return self.option_definition.option_type.value

    @property
    def maturity(self):
        """Returns option maturity."""
        return self.option_definition.expiry_date

    @property
    def strike(self):
        """Returns option strike."""
        return self.option_definition.strike

    @property
    def foreign_df(self):
        """Returns foreign discount factor."""
        return self.foreign_discounting_curve.discount_factor(
            self.valuation_date, self.maturity
        )

    @property
    def domestic_df(self):
        """Returns domestic discount factor."""
        return self.domestic_discounting_curve.discount_factor(
            self.valuation_date, self.maturity
        )

    @property
    def atm_forward(self):
        """Returns the forward contract strike F(0,T)."""
        return self.fx_spot * self.foreign_df / self.domestic_df

    def value(
        self,
        quote_convention: FxOptionQuoteConvention,
    ):
        """Prices the option"""
        undiscounted_price = self.omega * (
            self.atm_forward * norm.cdf(self.omega * self.d_plus)
            - self.strike * norm.cdf(self.omega * self.d_minus)
        )
        pv = self.domestic_df * undiscounted_price
        signed_pv = self.option_definition.direction * pv

        match quote_convention:
            case FxOptionQuoteConvention.DOMESTIC_PER_UNIT_OF_FOREIGN:
                return signed_pv * 100.0
            case FxOptionQuoteConvention.PERCENTAGE_DOMESTIC:
                return signed_pv / self.fx_spot * 100.0
            case FxOptionQuoteConvention.PERCENTAGE_FOREIGN:
                return signed_pv / self.strike * 100.0
            case FxOptionQuoteConvention.PERCENTAGE_DOMESTIC:
                return signed_pv / (self.fx_spot * self.strike) * 100
            case _:
                raise NotImplementedError(
                    f"Unsupported quote convention: {quote_convention}"
                )

    def delta(
        self,
        delta_convention: DeltaConvention = DeltaConvention.PIPS_SPOT_DELTA,
    ):
        """Calculates sensitivity to spot."""
        match delta_convention:
            case DeltaConvention.PIPS_SPOT_DELTA:
                return (
                    self.omega
                    * self.foreign_df
                    * norm.cdf(self.omega * self.d_plus)
                    * 100.00
                )
            case DeltaConvention.PIPS_FORWARD_DELTA:
                return self.omega * norm.cdf(self.omega * self.d_plus) * 100.0
            case DeltaConvention.PREMIUM_ADJUSTED_DELTA:
                pips_spot_delta = (
                    self.omega
                    * self.foreign_df
                    * norm.cdf(self.omega * self.d_plus)
                    * 100.00
                )
                value = self.value(FxOptionQuoteConvention.DOMESTIC_PER_UNIT_OF_FOREIGN)
                return pips_spot_delta - value / self.fx_spot

    def gamma(self):
        """Calculates curvature to spot."""
        return (
            self.foreign_df
            * norm.cdf(self.omega * self.d_plus())
            / (
                self.sigma
                * self.fx_spot
                * np.sqrt(Actual365.year_fraction(self.valuation_date, self.maturity))
            )
        )

    def theta(self):
        """Calculates sensitivity to time."""
        nd1 = norm.cdf(self.omega * self.d_plus)
        nd2 = norm.cdf(self.omega * self.d_minus)
        r_for = df_to_rate(self.foreign_df, self.valuation_date, self.maturity)
        r_dom = df_to_rate(self.domestic_df, self.valuation_date, self.maturity)
        return (
            self.omega
            * (
                self.fx_spot * r_for * self.foreign_df * nd1
                - self.strike * r_dom * self.domestic_df * nd2
            )
            - self.fx_spot
            * self.foreign_df
            * nd1
            * (
                self.sigma
                / (
                    2
                    * np.sqrt(
                        Actual365.year_fraction(self.valuation_date, self.maturity)
                    )
                )
            )
            * 100.0
        )

    def vega(self):
        """Calculates sensitivity to volatility."""
        return (
            self.fx_spot
            * self.foreign_df
            * norm.pdf(self.d_plus)
            * np.sqrt(Actual365.year_fraction(self.valuation_date, self.maturity))
        )

    def vanna(self):
        """Calculates second order sensitivity to volatility and spot."""
        return -self.foreign_df * norm.pdf(self.d_plus) * self.d_minus / self.sigma

    def volga(self):
        """Calculates curvature to volatility."""
        return (
            self.fx_spot
            * self.foreign_df
            * np.sqrt(Actual365.year_fraction(self.valuation_date, self.maturity))
            * norm.pdf(self.d_plus())
            * (self.d_plus() * self.d_minus())
            / self.sigma
        )
