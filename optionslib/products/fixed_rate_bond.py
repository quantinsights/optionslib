"""
This module provides support for valuing fixed rate bonds.
"""

from typing import List, Any
import attrs.validators
from attrs import field, define
import numpy as np

from optionslib.time.schedule import Schedule
from optionslib.types.var_types import NumericType
from optionslib.time.day_count_basis import DayCountBase


@define
class FixedRateBond:
    """
    An abstraction for a fixed-rate coupon-bearing bond
    that makes a stream of periodic coupon payments
    and principal repayment at maturity.
    """

    _isin: str = field(alias="isin", validator=attrs.validators.instance_of(str))

    _accrual_schedule: Schedule = field(
        alias="accrual_schedule", validator=attrs.validators.instance_of(Schedule)
    )

    _notionals: List[NumericType] | np.ndarray = field(alias="notionals")

    _coupon: NumericType = field(
        alias="coupon", validator=attrs.validators.instance_of(NumericType)
    )

    _accrual_basis: type(DayCountBase) = field(alias="accrual_basis")

    _frequency: int = field(
        alias="frequency",
        default=1,
        validator=attrs.validators.and_(
            attrs.validators.instance_of(int),
            attrs.validators.ge(1),
            attrs.validators.le(12),
        ),
    )

    @property
    def isin(self) -> str:
        """Get the bond ISIN identifier"""
        return self._isin

    @property
    def accrual_schedule(self) -> Schedule:
        """Get the underlying cashflow schedule"""
        return self._accrual_schedule

    @property
    def coupon(self) -> NumericType:
        """Get the fixed coupon rate"""
        return self._coupon

    @property
    def notionals(self) -> List[NumericType] | np.ndarray:
        """Get the bond notional (or array of notionals)"""
        return self._notionals

    @property
    def accrual_basis(self) -> Any:
        """Get the basis"""
        return self._accrual_basis

    @property
    def frequency(self) -> int:
        """Get the coupon frequency"""
        return self._frequency
