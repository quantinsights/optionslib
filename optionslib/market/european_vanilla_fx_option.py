"""A module for holding FX option market quotes."""
import datetime as dt
from datetime import date
from typing import List

import attrs
from attrs import define, field

from optionslib.types.enums import FxOptionsMarketQuote, OptionPayoff, Direction
from optionslib.types.var_types import NumericType


@define
class EuropeanVanillaFxOptionQuote:
    """Python dataclass for European Vanilla Fx Option Quote."""

    __foreign_ccy: str = field(validator=attrs.validators.instance_of(str))
    __domestic_ccy: str = field(validator=attrs.validators.instance_of(str))
    __as_of_date: dt.date = field(validator=attrs.validators.instance_of(dt.date))
    __expiry_date: dt.date = field(validator=attrs.validators.instance_of(dt.date))
    __strike: NumericType = field(validator=attrs.validators.instance_of(NumericType))
    __vol: NumericType = field(validator=attrs.validators.instance_of(NumericType))
    __quoteType: FxOptionsMarketQuote = field(
        validator=attrs.validators.instance_of(FxOptionsMarketQuote)
    )


class EuropeanVanillaFxOption:
    def __init__(
        self,
        tradeDate: date,
        expiryDate: date,
        strike: float,
        foreignCurrency: str,
        domesticCurrency: str,
        optionType: OptionPayoff,
        ccy1Notional: float = 1.0,
        direction: Direction = Direction.BUY,
    ):
        self.t0 = tradeDate
        self.T = expiryDate
        self.K = strike
        self.domesticCurrency = domesticCurrency
        self.foreignCurrency = foreignCurrency
        self.optionType = optionType
        self.ccy1Notional = ccy1Notional
        self.direction = direction


QuotesType = List[EuropeanVanillaFxOptionQuote]
