import datetime
from typing import Any, List

from src.basics.enums import FxVolatilitySurfaceParametricModel
from src.models.vanna_volga import VannaVolga
from european_vanilla_fx_option_quote import EuropeanVanillaFxOptionQuote
from src.basics.enums import FxOptionsMarketQuoteType


class FxVolatilitySurface:
    """
    An class representing the Fx Volatility surface, which is a scalar field
    F : R^2 -> R. The x-axis is the strike/moneyness of options and the y-axis
    is the time-to-expiration. The z-axis is the implied vol.

    A volatility surface can use any parametric model such as Vanna-Volga or
    SABR to compute vol. The underlying model is specified using
    fx_volatility_surface_parametric_model_type argument.
    """
    def __init__(self,
                 foreign_currency,
                 domestic_currency,
                 fx_option_market_quotes : List[EuropeanVanillaFxOptionQuote],
                 fx_volatility_surface_parametric_model_type : FxVolatilitySurfaceParametricModel
                 ):
        self.__foreign_currency = foreign_currency
        self.__domestic_currency = domestic_currency
        self.__fx_option_market_quotes = fx_option_market_quotes

        self.__valuation_date = fx_option_market_quotes[0].asOfDate if len(fx_option_market_quotes) > 0 else datetime.date.today()

        self.fxVolatilitySurfaceParametericModelType = fx_volatility_surface_parametric_model_type
        self.volSurfaceModel = self.getVolSurfaceModel()

    def getVolSurfaceModel(self) -> Any:
        if self.fxVolatilitySurfaceParametericModel == FxVolatilitySurfaceParametricModel.VANNA_VOLGA:
            # Instantantiate the VannaVolga and calibrate the surface to market quotes
            # of straddles, risk-reversals and fly's.
            return VannaVolga(
                self.__fx_option_market_quotes
            )

    def getVolatility(self, strike: float, maturity:datetime.date)->float:
        pass