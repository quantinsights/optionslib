from enum import IntEnum, StrEnum


class RollConventions(IntEnum):
    """
    The purpose of this convention is to define how to roll dates when building a schedule.
    The standard approach in building a schedule is to start with a base unadjusted date (one that does not
    have a business day convention applied). To get the next date in the schedule, we take the base date
    and the coupon tenor. Once this date is calculated, a roll-convention is applied to compute the
    next schedule date.
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
    When processing dates in finance, a cashflow cannot occur on a business holiday. So, any non-business
    dates have to be converted to a nearby valid business date. The business day convention together with the
    holiday calendar defines exactly how this adjustment is to be made.
    """

    NO_ADJUST = "No adjustment"
    MODIFIED_FOLLOWING = "Modified Following"
    FOLLOWING = "Following"
    PRECEDING = "Preceding"
    MODIFIED_PRECEDING = "Modified Preceding"


class DayOfWeek(IntEnum):
    """
    Named constants for the days of the week.
    """

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class HolidayCalendarId(StrEnum):
    """
    List of supported holiday calendar IDs
    """

    TARGET = "Target"
    US = "US"
    LONDON = "London"


class Period(StrEnum):
    """
    A calendar period such as days, business days, months or years
    """

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
