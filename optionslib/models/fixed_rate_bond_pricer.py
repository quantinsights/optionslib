"""A pricer for fixed rate bonds."""


import datetime as dt
from typing import Optional
import numpy as np
import scipy.optimize
import attrs
from attrs import define,field

from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.products.fixed_rate_bond import FixedRateBond
from optionslib.types.var_types import NumericType


@define
class FixedRateBondPricer:
    """A pricer for fixed coupon bonds."""

    _pv_date: dt.date = field(
        alias="pv_date", validator=attrs.validators.instance_of(dt.date)
    )

    _bond: FixedRateBond = field(
        alias="bond", validator=attrs.validators.instance_of(FixedRateBond)
    )

    _discounting_curve: DiscountingCurve = field(
        alias="discounting_curve",
        validator=attrs.validators.instance_of(DiscountingCurve),
    )

    _z_spread: Optional[NumericType] = field(
        alias="z_spread",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    _clean_price: Optional[NumericType] = field(
        alias="clean_price",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    _dirty_price: Optional[NumericType] = field(
        alias="dirty_price",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    _yield_to_maturity: Optional[NumericType] = field(
        alias="yield_to_maturity",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    _is_bullet: bool = field(init=False)
    _coupon_idx: int = field(init=False)
    _notionals_per_coupon: np.ndarray = field(init=False)
    _notional_repayment: np.array = field(init=False)

    def __attrs_post_init__(self):
        self._is_bullet = len(self.bond.notionals) == 1

        periods = self.bond.accrual_schedule.schedule_periods
        self._coupon_idx = next(
            i
            for i in range(len(periods))
            if periods[i].adjusted_end_date > self.pv_date
        )

        if self._is_bullet:
            self._notionals_per_coupon = np.empty(
                len(self.bond.accrual_schedule.schedule_periods)
            )
            self._notionals_per_coupon.fill(self.bond.notionals[0])
            self._notionals_per_coupon = np.concatenate(
                (self._notionals_per_coupon, np.array([0])), axis=0
            )
        else:
            self._notionals_per_coupon = self.bond.notionals

        self._notional_repayment = np.array(
            [
                self._notionals_per_coupon[i] - self._notionals_per_coupon[i + 1]
                for i in range(len(self.bond.accrual_schedule.schedule_periods))
            ]
        )

    @property
    def pv_date(self) -> dt.date:
        """Get the pv date."""
        return self._pv_date

    @property
    def bond(self) -> FixedRateBond:
        """Get the fixed rate bond instrument."""
        return self._bond

    @property
    def discounting_curve(self) -> DiscountingCurve:
        """Get the risk-free discounting curve."""
        return self._discounting_curve

    @property
    def z_spread(self):
        """Get the z-spread for the bond."""
        return self._z_spread

    @property
    def clean_price(self):
        """Get the clean price of the bond."""
        return self._clean_price

    def accrued_interest(self):
        """Convert the clean-price to a dirty price."""
        accrual_start_date = self.bond.accrual_schedule.schedule_periods[
            self._coupon_idx
        ].adjusted_start_date
        bond_settle_date = self.pv_date + dt.timedelta(days=2)

        accrual_fraction = (
            self.bond.accrual_basis.year_fraction(accrual_start_date, bond_settle_date)
            * self.bond.frequency
        )

        full_coupon = (
            self._notionals_per_coupon[self._coupon_idx]
            * self.bond.coupon
            / self.bond.frequency
        )

        accrued_interest = full_coupon * accrual_fraction

        # Normalize the interest accrued by the notional
        return accrued_interest / self._notionals_per_coupon[self._coupon_idx]

    def clean_price_to_dirty_price(self):
        """Convert the clean-price to a dirty price."""

        if self._clean_price > 0.0:

            self._dirty_price = self._clean_price + self.accrued_interest()

            return self._dirty_price

        return None

    def dirty_price_to_clean_price(self):
        """Convert the dirty-price to a clean price."""

        if self._dirty_price > 0.0:

            self._clean_price = self._dirty_price + self.accrued_interest()

            return self._clean_price

        return None

    def clean_price_to_yield(self) -> Optional[float]:
        """
        Solves for the yield of the bond, given a clean price.
        """
        if self._clean_price > 0.0:

            def f(x):
                return self.yield_to_clean_price(x) - self._clean_price

            yld = scipy.optimize.newton(f, 0.001, tol=1e-6)
            return yld

        return None

    def yield_to_clean_price(self, yield_to_mat: float) -> float:
        """
        Convert the YTM of a bond to a clean price.
        """
        pv = 0.0
        df = 1.0
        num_of_periods = 1

        max_iter = len(self.bond.accrual_schedule.schedule_periods)

        for i in range(self._coupon_idx, max_iter):

            df = 1.0 / (1 + yield_to_mat / self.bond.frequency) ** num_of_periods
            pv += df * (
                self.bond.coupon / self.bond.frequency * self._notionals_per_coupon[i]
                + self._notional_repayment[i]
            )
            num_of_periods += 1

        # Normalization
        return pv / self._notionals_per_coupon[0]


