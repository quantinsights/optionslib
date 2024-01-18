"""
This module contains global-accessible enums.
"""
from enum import Enum, IntEnum, StrEnum, auto


class Direction(IntEnum):
    """Trade direction"""

    BUY = 1
    SELL = -1


class FxVanillaEuropeanOptionQuoteConvention(IntEnum):
    """Fx option quote conventions"""

    DOMESTIC_PER_UNIT_OF_FOREIGN = auto()
    PERCENTAGE_FOREIGN = auto()
    PERCENTAGE_DOMESTIC = auto()
    FOREIGN_PER_UNIT_OF_DOMESTIC = auto()


class DeltaConvention(IntEnum):
    """Delta conventions in the FX Options market"""

    PIPS_SPOT_DELTA = auto()
    PIPS_FORWARD_DELTA = auto()
    PREMIUM_ADJUSTED_DELTA = auto()


class FxVolatilitySurfaceParametricModel(IntEnum):
    """The type of volatility surface parameteric model"""

    VANNA_VOLGA = auto()
    SABR = auto()
    HESTON = auto()


class FxOptionsMarketQuoteType(StrEnum):
    """The type of options market quote"""

    ATM_STRADDLE = "STDL"
    TWENTY_FIVE_DELTA_RISK_REVERSAL = "25DRR"
    TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY = "25DFLY"
    TWENTY_FIVE_DELTA_CALL = "25DCALL"
    TWENTY_FIVE_DELTA_PUT = "25DPUT"
    TEN_DELTA_RISK_REVERSAL = "10DRR"
    TEN_DELTA_VEGA_WEIGHTED_BUTTERFLY = "10FLY"


class OptionType(Enum):
    CALL_OPTION = 1
    PUT_OPTION = 2


class DiscountingInterpolationMethod(IntEnum):
    LINEAR_ON_DISCOUNT_FACTORS = auto()
    LINEAR_ON_RATES = auto()
    LINEAR_ON_LOG_OF_RATES = auto()
    LINEAR_ON_LOG_OF_DISCOUNT_FACTORS = auto()
    NATURAL_CUBIC_SPLINE = auto()
    BESSEL_CUBIC_SPLINE = auto()
    FINANCIAL_CUBIC_SPLINE = auto()
    QUARTIC_SPLINE = auto()
