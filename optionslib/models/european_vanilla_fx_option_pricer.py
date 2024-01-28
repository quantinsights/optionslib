"""Option pricer using Black calculator."""

import datetime as dt

from attr import define

from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.products.european_vanilla_fx_option import EuropeanVanillaFxOption
from optionslib.market.fx_volatility_surface import FxVolatilitySurface
from optionslib.models.black_calculator import BlackCalculator


@define
class EuropeanVanillaFxOptionPricer:
    """A pricer for European Vanilla FX Options that uses the `BlackCalculator`.

    Once initialized acts like callable returning Black calculator
    with volatility set from surface.
    """

    valuationDate: dt.date
    europeanVanillaFxOption: EuropeanVanillaFxOption
    fxSpot: float
    foreignDiscountingCurve: DiscountingCurve
    domesticDiscountingCurve: DiscountingCurve
    fxVolatilitySurface: FxVolatilitySurface

    def __call__(self, strike, maturity):
        """Returns Black calculator."""
        sigma = self.fxVolatilitySurface.volatility(strike, maturity).sigma
        return BlackCalculator(
            self.valuationDate,
            self.europeanVanillaFxOption,
            self.fxSpot,
            self.foreignDiscountingCurve,
            self.domesticDiscountingCurve,
            sigma,
        )
