"""
A module for holding FX option market quotes.
"""
import datetime as dt
from typing import Union
import numpy as np
from attrs import define, field
import attrs

from src.basics.enums import FxOptionsMarketQuoteType

NumericType = Union[int, float, np.number]

@define
class EuropeanVanillaFxOptionQuote:
    """Python dataclass for European Vanilla Fx Option Quote"""

    __foreign_ccy : str = field(validator=attrs.validators.instance_of(str))
    __domestic_ccy : str = field(validator=attrs.validators.instance_of(str))
    __as_of_date : dt.date = field(validator=attrs.validators.instance_of(dt.date))
    __expiry_date : dt.date = field(validator=attrs.validators.instance_of(dt.date))
    __strike : NumericType = field(validator=attrs.validators.instance_of(NumericType))
    __vol: NumericType = field(validator=attrs.validators.instance_of(NumericType))
    __quoteType : FxOptionsMarketQuoteType(
        validator=attrs.validators.instance_of(FxOptionsMarketQuoteType)
    )
