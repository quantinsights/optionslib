"""A pricer for fixed rate bonds."""

import datetime as dt
from typing import Optional
import numpy as np
import scipy.optimize
import attrs
from attrs import define, field

from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.products.fixed_rate_bond import FixedRateBond
from optionslib.types.var_types import NumericType


@define
class FixedRateBondPricer:
    """A pricer for fixed coupon bonds."""

    pv_date: dt.date = field(
        alias="pv_date", validator=attrs.validators.instance_of(dt.date)
    )

    bond: FixedRateBond = field(
        alias="bond", validator=attrs.validators.instance_of(FixedRateBond)
    )

    discounting_curve: DiscountingCurve = field(
        alias="discounting_curve",
        validator=attrs.validators.instance_of(DiscountingCurve),
    )

    z_spread: Optional[NumericType] = field(
        alias="z_spread",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    clean_price: Optional[NumericType] = field(
        alias="clean_price",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    dirty_price: Optional[NumericType] = field(
        alias="dirty_price",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    yield_to_maturity: Optional[NumericType] = field(
        alias="yield_to_maturity",
        default=None,
        validator=attrs.validators.instance_of(Optional[NumericType]),
    )

    # internal
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

        if self.clean_price > 0.0:

            self.dirty_price = self.clean_price + self.accrued_interest()

            return self.dirty_price

        return None

    def dirty_price_to_clean_price(self):
        """Convert the dirty-price to a clean price."""

        if self.dirty_price > 0.0:

            self.clean_price = self.dirty_price + self.accrued_interest()

            return self.clean_price

        return None

    def clean_price_to_yield(self) -> Optional[float]:
        """Solves for the yield of the bond, given a clean price."""
        if self.clean_price > 0.0:

            def f(x):
                return self.yield_to_clean_price(x) - self.clean_price

            yld = scipy.optimize.newton(f, 0.001, tol=1e-6)
            return yld

        return None

    def yield_to_clean_price(self, yield_to_mat: float) -> float:
        """Convert the YTM of a bond to a clean price."""
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
        return pv / self._notionals_per_coupon[self._coupon_idx]

    def pv(self):
        """Compute the PV of bond using the risk-free discounting curve and z-spread."""
        if not (self.discounting_curve or self.z_spread):
            raise ValueError(
                "The risk-free discounting curve and z-spread must be supplied!"
            )

        discounting_curve_to_use: DiscountingCurve = self.discounting_curve.add_spread(
            self.z_spread
        )
        pv = 0.0

        max_iter = len(self.bond.accrual_schedule.schedule_periods)

        for i in range(self._coupon_idx, max_iter):
            accrual_end_date = self.bond.accrual_schedule.schedule_periods[
                i
            ].adjusted_end_date

            df = discounting_curve_to_use.discount_factor(
                self.pv_date, accrual_end_date
            )
            pv += df * (
                self.bond.coupon / self.bond.frequency * self._notionals_per_coupon[i]
                + self._notional_repayment[i]
            )

        return pv

    def dv01(self):
        """
        Compute the numerical derivative
        dP/dy = (P(y+0.0001) - P(y))/0.0001
        """
        delta = 0.0001
        x_0 = self.yield_to_maturity
        funct = self.yield_to_clean_price

        return (funct(x_0 + delta) - funct(x_0)) / delta

    def convexity(self):
        """Compute the central difference d2P/dy2 = P(y+0.0001)-2P(y) +
        P(y-0.0001)/(0.0001^2)"""
        delta = 0.0001
        x_0 = self.yield_to_maturity
        funct = self.yield_to_clean_price

        return (funct(x_0 + delta) - 2 * funct(x_0) + funct(x_0 - delta)) / delta**2
