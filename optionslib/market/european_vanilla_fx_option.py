"""A module for holding FX option market quotes."""

import datetime as dt
from typing import List

import attrs
from attrs import define, field

from optionslib.types.enums import FxOptionsMarketQuote, OptionPayoff, Direction
from optionslib.types.var_types import NumericType


@define
class EuropeanVanillaFxOptionQuote:
    """Python dataclass for European Vanilla Fx Option Quote."""

    foreign_ccy: str = field(validator=attrs.validators.instance_of(str))
    domestic_ccy: str = field(validator=attrs.validators.instance_of(str))
    as_of_date: dt.date = field(validator=attrs.validators.instance_of(dt.date))
    expiry_date: dt.date = field(validator=attrs.validators.instance_of(dt.date))
    strike: NumericType = field(validator=attrs.validators.instance_of(NumericType))
    vol: NumericType = field(validator=attrs.validators.instance_of(NumericType))
    quote_type: FxOptionsMarketQuote = field(
        validator=attrs.validators.instance_of(FxOptionsMarketQuote)
    )


@define
class EuropeanVanillaFxOption:
    """Class to represent European option instrument."""

    trade_date: dt.date
    expiry_date: dt.date
    strike: float
    foreign_currency: str
    domestic_currency: str
    option_type: OptionPayoff
    ccy1_notional: float = field(default=1.0)
    direction: Direction = field(default=Direction.BUY)


QuotesListType = List[EuropeanVanillaFxOptionQuote]
