"""Option pricer using Black calculator."""

import datetime as dt

from attr import define

from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.market.fx_volatility_surface import FxVolatilitySurface
from optionslib.models.black_calculator import BlackCalculator
from optionslib.products.european_vanilla_fx_option import EuropeanVanillaFxOption


@define
class EuropeanVanillaFxOptionPricer:
    """
    A pricer for European Vanilla FX Options that uses the `BlackCalculator`.

    Once initialized acts like callable returning Black calculator with volatility set
    from surface.

    """

    domestic_discounting_curve: DiscountingCurve
    european_vanilla_fx_option: EuropeanVanillaFxOption
    foreign_discounting_curve: DiscountingCurve
    fx_spot: float
    fx_volatility_surface: FxVolatilitySurface
    valuation_date: dt.date

    def __call__(self, strike, maturity):
        """Returns Black calculator."""
        sigma = self.fx_volatility_surface.volatility(strike, maturity).sigma
        return BlackCalculator(
            self.valuation_date,
            self.european_vanilla_fx_option,
            self.fx_spot,
            self.foreign_discounting_curve,
            self.domestic_discounting_curve,
            sigma,
        )
