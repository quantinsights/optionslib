from datetime import date
from basics.Enums import FxOptionsMarketQuoteType
class EuropeanVanillaFxOptionQuote:
    def __init__(
            self,
            foreignCurrency : str,
            domesticCurrency : str,
            asOfDate : date,
            expiryDate : date,
            strike : float,
            vol : float,
            quoteType : FxOptionsMarketQuoteType
    ):
        self.foreignCcy = foreignCurrency
        self.domesticCcy = domesticCurrency
        self.asOfDate = asOfDate
        self.expiryDate = expiryDate
        self.strike = strike
        self.vol = vol
        self.quoteType = quoteType