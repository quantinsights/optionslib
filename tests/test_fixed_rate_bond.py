import datetime as dt
import unittest

import numpy as np
import matplotlib.pyplot as plt

from optionslib.types.enums import (
    Period,
    StubConvention,
    DiscountingInterpolationMethod,
)
from optionslib.time.frequency import Frequency
from optionslib.time.schedule import Schedule, SchedulePeriod
from optionslib.time.schedule import Schedule
from optionslib.products.fixed_rate_bond import FixedRateBond
from optionslib.market.discounting_curve import DiscountingCurve
from optionslib.models.fixed_rate_bond_pricer import FixedRateBondPricer
from optionslib.time.day_count_basis import Thirty360


class TestFixedRateBond(unittest.TestCase):
    def setUp(self) -> None:
        self.bond_schedule = Schedule(
            start_date=dt.date(2019, 4, 16),
            end_date=dt.date(2039, 4, 16),
            frequency=Frequency(6, Period.MONTHS),
            stub_convention=StubConvention.NONE,
        )

        self.bond = FixedRateBond(
            isin="XS1982113463",
            accrual_schedule=self.bond_schedule,
            notionals=[10e6],
            coupon=0.0425,
            accrual_basis=Thirty360,
            frequency=2,
        )

        # mocked discounting curve
        self.discounting_curve = DiscountingCurve(
            dates=[
                dt.date(2024, 1, 23),
                dt.date(2024, 4, 16),
                dt.date(2024, 10, 16),
                dt.date(2025, 4, 16),
                dt.date(2025, 10, 16),
                dt.date(2026, 4, 16),
                dt.date(2026, 10, 16),
                dt.date(2027, 4, 16),
                dt.date(2027, 10, 16),
                dt.date(2028, 4, 16),
                dt.date(2028, 10, 16),
                dt.date(2029, 4, 16),
                dt.date(2029, 10, 16),
                dt.date(2030, 4, 16),
                dt.date(2030, 10, 16),
                dt.date(2031, 4, 16),
                dt.date(2031, 10, 16),
                dt.date(2032, 4, 16),
                dt.date(2032, 10, 16),
                dt.date(2033, 4, 16),
                dt.date(2033, 10, 16),
                dt.date(2034, 4, 16),
                dt.date(2034, 10, 16),
                dt.date(2035, 4, 16),
                dt.date(2035, 10, 16),
                dt.date(2036, 4, 16),
                dt.date(2036, 10, 16),
                dt.date(2037, 4, 16),
                dt.date(2037, 10, 16),
                dt.date(2038, 4, 16),
                dt.date(2038, 10, 16),
                dt.date(2039, 4, 16),
            ],
            discount_factors=[np.exp(-0.04 * t / 2) for t in range(32)],
            interpolation_method=DiscountingInterpolationMethod.LINEAR_ON_LOG_OF_DISCOUNT_FACTORS,
        )

        self.pricer = FixedRateBondPricer(
            pv_date=dt.date(2024, 1, 23),
            bond=self.bond,
            discounting_curve=self.discounting_curve,
            clean_price=0.994735,
            z_spread=0.00256,
        )

    def test_fixed_rate_bond_price_to_par(self):
        # Price to par
        self.assertAlmostEqual(
            self.pricer.yield_to_clean_price(yield_to_mat=0.0425),
            1.00,
            places=7,
            msg="Failed test_fixed_rate_bond_price_to_par, the clean price did not equal par value!",
        )

    def test_fixed_rate_bond_yield(self):
        # Determine the yield of the bond
        self.assertAlmostEqual(
            self.pricer.clean_price_to_yield(),
            0.0429697088258,
            places=5,
            msg="Failed test_fixed_rate_bond_price_to_par, the yield must 4.2970%!",
        )

    def test_fixed_rate_bond_clean_to_dirty(self):
        # Convert the clean price of the bond to a dirty price
        self.assertAlmostEqual(
            self.pricer.clean_price_to_dirty_price(),
            1.0064225,
            places=7,
            msg="Failed test_fixed_rate_bond_clean_to_dirty, the dirty price must be 4.970%!",
        )

    def test_fixed_rate_bond_accrued_interest(self):
        # Compute the accrued interest, since we are mid-coupon
        self.assertAlmostEqual(
            self.pricer.accrued_interest(),
            0.0116875,
            places=5,
            msg="Failed test_fixed_rate_bond_accrued_interest, the accrued interest must be 1.116875%",
        )

    def test_fixed_rate_bond_pv(self):
        # Compute the pv of the bond
        self.assertAlmostEqual(
            self.pricer.pv() / 10e6,
            0.994735,
            places=3,
            msg="Failed test_fixed_rate_bond_accrued_interest, the pv must be 99.4735%!",
        )
