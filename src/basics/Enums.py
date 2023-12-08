from enum import Enum,IntEnum,StrEnum

class Direction(IntEnum):
    BUY = 1
    SELL = -1

class FxVanillaEuropeanOptionQuoteConvention(IntEnum):
    DOMESTIC_PER_UNIT_OF_FOREIGN = 1
    PERCENTAGE_FOREIGN = 2
    PERCENTAGE_DOMESTIC = 3
    FOREIGN_PER_UNIT_OF_DOMESTIC = 4

class DeltaConvention(IntEnum):
    PIPS_SPOT_DELTA = 1
    PIPS_FORWARD_DELTA = 2
    PREMIUM_ADJUSTED_DELTA = 3

class FxVolatilitySurfaceParametricModel(IntEnum):
    VANNA_VOLGA = 1
    SABR = 2
    HESTON = 3

class FxOptionsMarketQuoteType(StrEnum):
    ATM_STRADDLE = 'STDL'
    TWENTY_FIVE_DELTA_RISK_REVERSAL = '25DRR'
    TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY = '25DFLY'
    TWENTY_FIVE_DELTA_CALL = '25DCALL'
    TWENTY_FIVE_DELTA_PUT = '25DPUT'
    TEN_DELTA_RISK_REVERSAL = '10DRR'
    TEN_DELTA_VEGA_WEIGHTED_BUTTERFLY = '10FLY'
