"""This module contains functionality that supports volatility surfaces for FX
options markets."""
import datetime as dt
from typing import List

import attrs
from attrs import define, field

from optionslib.market.european_vanilla_fx_option import EuropeanVanillaFxOptionQuote
from optionslib.models.vanna_volga import VannaVolga, VolatilitySurfaceModel
from optionslib.types.enums import FxVolatilitySurfaceParametricModel


@define
class FxVolatilitySurfacePoint:
    """Represents a point on the volatility surface sigma(T,K)"""

    __k: float = field(validator=attrs.validators.instance_of(float))
    __t: dt.date = field(validator=attrs.validators.instance_of(dt.date))
    __sigma: float = field(validator=attrs.validators.instance_of(float))

    @property
    def k(self) -> float:
        """Return the strike."""
        return self.__k

    @property
    def t(self) -> dt.date:
        """Return the expiration date."""
        return self.__t

    @property
    def sigma(self) -> float:
        """Returns the implied vol."""
        return self.__sigma


@define
class FxVolatilitySurface:
    """
    An class representing the Fx Volatility surface, which is a scalar field
    F : R^2 -> R. The x-axis is the strike/moneyness of options and the y-axis
    is the time-to-expiration. The z-axis is the implied vol.

    A volatility surface can use any parametric model such as Vanna-Volga or
    SABR to compute vol. The underlying model is specified using
    fx_volatility_surface_parametric_model_type argument.
    """

    __fx_option_market_quotes: EuropeanVanillaFxOptionQuote = field(
        validator=attrs.validators.instance_of(List[EuropeanVanillaFxOptionQuote])
    )
    __fx_volatility_surface_parametric_model_type: FxVolatilitySurfaceParametricModel = field(
        validator=attrs.validators.instance_of(FxVolatilitySurfaceParametricModel)
    )
    __foreign_currency: str = field(
        default="EUR", validator=attrs.validators.instance_of(str)
    )
    __domestic_currency: str = field(
        default="USD", validator=attrs.validators.instance_of(str)
    )

    def __attrs_post_init__(self):
        """Post initialization."""
        self.__valuation_date = (
            self.__fx_option_market_quotes[0].asOfDate
            if len(self.__fx_option_market_quotes) > 0
            else dt.date.today()
        )

        self.__vol_surface_model = self.init_vol_surface_model()

    @property
    def foreign_ccy(self) -> str:
        """Return the foreign ccy."""
        return self.__foreign_currency

    @property
    def domestic_ccy(self) -> str:
        """Return the domestic ccy."""
        return self.__domestic_currency

    @property
    def fx_option_market_quotes(self) -> List[EuropeanVanillaFxOptionQuote]:
        """Return the Fx Option market quotes."""
        return self.__fx_option_market_quotes

    @property
    def fx_volatility_surface_parametric_model_type(
        self,
    ) -> FxVolatilitySurfaceParametricModel:
        """Return the volatility surface parameteric model type."""
        return self.__fx_volatility_surface_parametric_model_type

    @property
    def vol_surface_model(self) -> VolatilitySurfaceModel:
        """Returns the volatility surface model object."""
        return self.__vol_surface_model

    @property
    def valuation_date(self) -> dt.datetime:
        """Return the valuation date."""
        return self.__valuation_date

    def init_vol_surface_model(self) -> VolatilitySurfaceModel:
        """Initialize a vol surface model with options market quotes."""
        if (
            self.fx_volatility_surface_parametric_model_type
            == FxVolatilitySurfaceParametricModel.VANNA_VOLGA
        ):
            # Instantantiate the VannaVolga and calibrate the surface to market quotes
            # of straddles, risk-reversals and fly's.
            return VannaVolga(self.fx_option_market_quotes)

    def volatility(self, strike: float, maturity: dt.date) -> FxVolatilitySurfacePoint:
        """Returns the implied vol from underlying fitted vol model."""
        if (
            self.fx_volatility_surface_parametric_model_type
            == FxVolatilitySurfaceParametricModel.VANNA_VOLGA
        ):
            vol = self.vol_surface_model.second_order_approximation(strike, maturity)
            return FxVolatilitySurfacePoint(strike, maturity, vol)
