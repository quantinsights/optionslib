import datetime
from typing import Any, List
from basics.Enums import FxVolatilitySurfaceParametricModel
from models.VannaVolga import VannaVolga
from EuropeanVanillaFxOptionQuote import EuropeanVanillaFxOptionQuote
from basics.Enums import FxOptionsMarketQuoteType

## An abstraction for the FX volatility surface for a currency pair.
class FxVolatilitySurface:
    def __init__(self,
                 foreignCurrency,
                 domesticCurrency,
                 fxOptionMarketQuotes : List[EuropeanVanillaFxOptionQuote],
                 fxVolatilitySurfaceParametricModel : FxVolatilitySurfaceParametricModel
    ):
        self.foreignCurrency = foreignCurrency
        self.domesticCurrency = domesticCurrency
        self.fxOptionMarketQuotes = fxOptionMarketQuotes

        self.valuationDate = fxOptionMarketQuotes[0].asOfDate if len(fxOptionMarketQuotes) > 0 else datetime.date.today()

        self.fxVolatilitySurfaceParametericModelType = fxVolatilitySurfaceParametricModel
        self.volSurfaceModel = self.getVolSurfaceModel()

    def getVolSurfaceModel(self) -> Any:
        if self.fxVolatilitySurfaceParametericModel == FxVolatilitySurfaceParametricModel.VANNA_VOLGA:
            # Instantantiate the VannaVolga and calibrate the surface to market quotes
            # of straddles, risk-reversals and fly's.
            return VannaVolga(
                self.fxOptionMarketQuotes
            )

    def getVolatility(self, strike: float, maturity:datetime.date)->float:
        pass