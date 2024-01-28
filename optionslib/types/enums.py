"""This module contains global-accessible enums."""

from enum import Enum, IntEnum, StrEnum, auto


class Direction(IntEnum):
    """Trade direction."""

    BUY = 1
    SELL = -1


class FxOptionQuoteConvention(IntEnum):
    """Fx option quote conventions."""

    DOMESTIC_PER_UNIT_OF_FOREIGN = auto()
    PERCENTAGE_FOREIGN = auto()
    PERCENTAGE_DOMESTIC = auto()
    FOREIGN_PER_UNIT_OF_DOMESTIC = auto()


class DeltaConvention(IntEnum):
    """Delta conventions in the FX Options market."""

    PIPS_SPOT_DELTA = auto()
    PIPS_FORWARD_DELTA = auto()
    PREMIUM_ADJUSTED_DELTA = auto()


class FxVolatilitySurfaceParametricModel(IntEnum):
    """The model of volatility surface parameteric model."""

    VANNA_VOLGA = auto()
    SABR = auto()
    HESTON = auto()


class FxOptionsMarketQuote(StrEnum):
    """The style of options market quote."""

    ATM_STRADDLE = "STDL"
    TWENTY_FIVE_DELTA_RISK_REVERSAL = "25DRR"
    TWENTY_FIVE_DELTA_VEGA_WEIGHTED_BUTTERFLY = "25DFLY"
    TWENTY_FIVE_DELTA_CALL = "25DCALL"
    TWENTY_FIVE_DELTA_PUT = "25DPUT"
    TEN_DELTA_RISK_REVERSAL = "10DRR"
    TEN_DELTA_VEGA_WEIGHTED_BUTTERFLY = "10FLY"


class OptionPayoff(Enum):
    """The payoff style of option contract."""

    CALL_OPTION = 1
    PUT_OPTION = 2


class DiscountingInterpolationMethod(IntEnum):
    """The discounting interpolation method for discount curve."""

    LINEAR_ON_DISCOUNT_FACTORS = auto()
    LINEAR_ON_RATES = auto()
    LINEAR_ON_LOG_OF_RATES = auto()
    LINEAR_ON_LOG_OF_DISCOUNT_FACTORS = auto()
    NATURAL_CUBIC_SPLINE = auto()
    BESSEL_CUBIC_SPLINE = auto()
    FINANCIAL_CUBIC_SPLINE = auto()
    QUARTIC_SPLINE = auto()


class RollConventions(IntEnum):
    """
    The purpose of this convention is to define how to roll dates when building a
    schedule.

    The standard approach in building a schedule is to start with a base unadjusted date
    (one that does not have a business day convention applied). To get the next date in
    the schedule, we take the base date and the coupon tenor. Once this date is
    calculated, a roll- convention is applied to compute the next schedule date.

    """

    DAY_1 = (1,)
    DAY_2 = (2,)
    DAY_3 = (3,)
    DAY_4 = (4,)
    DAY_5 = (5,)
    DAY_6 = (6,)
    DAY_7 = (7,)
    DAY_8 = (8,)
    DAY_9 = (9,)
    DAY10 = (10,)
    DAY11 = (11,)
    DAY12 = (12,)
    DAY_13 = (13,)
    DAY_14 = (14,)
    DAY_15 = (15,)
    DAY_16 = (16,)
    DAY_17 = (17,)
    DAY_18 = (18,)
    DAY_19 = (19,)
    DAY_20 = (20,)
    DAY_21 = (21,)
    DAY_22 = (22,)
    DAY_23 = (23,)
    DAY_24 = (24,)
    DAY_25 = (25,)
    DAY_26 = (26,)
    DAY_27 = (27,)
    DAY_28 = (28,)
    DAY_29 = (29,)
    DAY_30 = (30,)
    EOM = (31,)
    NONE = (0,)
    IMM = (100,)
    DAY_SUN = (101,)
    DAY_MON = (102,)
    DAY_TUE = (103,)
    DAY_WED = (104,)
    DAY_THU = (105,)
    DAY_FRI = (106,)
    DAY_SAT = 107


class BusinessDayConventions(StrEnum):
    """
    When processing dates in finance, a cashflow cannot occur on a business holiday.

    So, any non-business dates have to be converted to a nearby valid business date. The
    business day convention together with the holiday calendar defines exactly how this
    adjustment is to be made.

    """

    NO_ADJUST = "No adjustment"
    MODIFIED_FOLLOWING = "Modified Following"
    FOLLOWING = "Following"
    PRECEDING = "Preceding"
    MODIFIED_PRECEDING = "Modified Preceding"


class DayOfWeek(IntEnum):
    """Named constants for the days of the week."""

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class HolidayCalendarId(StrEnum):
    """List of supported holiday calendar IDs."""

    TARGET = "Target"
    US = "US"
    LONDON = "London"


class Period(StrEnum):
    """A calendar period such as days, business days, months or years."""

    BUSINESS_DAYS = "business days"
    DAYS = "days"
    MONTHS = "months"
    YEARS = "years"


class StubConvention(StrEnum):
    """
    A stub is an irregular period in the front or rear of the schedule.

    The StubConvention determines how a stub is created during schedule generation.

    """

    NONE = "None"
    SHORT_INITIAL = "Short Initial"
    LONG_INITIAL = "Long Initial"
    SHORT_FINAL = "Short Final"
    LONG_FINAL = "Long Final"
    BOTH = "Both"


class BondQuoteConvention(StrEnum):
    """
    A bond mark could be one of several types:
    - yield
    - z-spread on top of a sovereign risk-free curve
    - clean price
    - dirty price
    """

    YIELD = "Yield"
    Z_SPREAD = "Z-Spread"
    CLEAN_PRICE = "Clean-price"
    DIRTY_PRICE = "Dirty-Price"
