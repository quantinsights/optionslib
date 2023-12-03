from enum import Enum
from datetime import date
from basics.DayCountBasis import Actual365
from basics.Enums import Direction

class OptionType(Enum):
    CALL_OPTION = 1
    PUT_OPTION = 2

class EuropeanVanillaFxOption:
    def __init__(
            self,
            tradeDate : date,
            expiryDate : date,
            strike : float,
            foreignCurrency : str,
            domesticCurrency : str,
            optionType : OptionType,
            ccy1Notional : float = 1.0,
            direction : Direction = Direction.BUY,
    ):
        self.t0 = tradeDate
        self.T = expiryDate
        self.K = strike
        self.domesticCurrency = domesticCurrency
        self.foreignCurrency = foreignCurrency
        self.optionType = optionType
        self.ccy1Notional = ccy1Notional
        self.direction = direction