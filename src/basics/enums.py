from enum import Enum,IntEnum,StrEnum,auto

class Direction(IntEnum):
    BUY = 1
    SELL = -1

class FxVanillaEuropeanOptionQuoteConvention(IntEnum):
    DOMESTIC_PER_UNIT_OF_FOREIGN = auto()
    PERCENTAGE_FOREIGN = auto()
    PERCENTAGE_DOMESTIC = auto()
    FOREIGN_PER_UNIT_OF_DOMESTIC = auto()

class DeltaConvention(IntEnum):
    PIPS_SPOT_DELTA = auto()
    PIPS_FORWARD_DELTA = auto()
    PREMIUM_ADJUSTED_DELTA = auto()

class FxVolatilitySurfaceParametricModel(IntEnum):
    VANNA_VOLGA = auto()
    SABR = auto()
    HESTON = auto()

class FxOptionsMarketQuoteType(StrEnum):
    ATM_STRADDLE = 'STDL'
    TWENTY_FIVE_DELTA_RISK_REVERSAL = '25DRR'
    TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY = '25DFLY'
    TWENTY_FIVE_DELTA_CALL = '25DCALL'
    TWENTY_FIVE_DELTA_PUT = '25DPUT'
    TEN_DELTA_RISK_REVERSAL = '10DRR'
    TEN_DELTA_VEGA_WEIGHTED_BUTTERFLY = '10FLY'
