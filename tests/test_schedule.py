import unittest
import datetime as dt

from src.basics.enums import Period, StubConvention
from src.basics.frequency import Frequency
from src.basics.schedule import Schedule, SchedulePeriod


class TestSchedule(unittest.TestCase):
    """Unit tests for Schedule"""

    def test_short_final(self):
        """Unit test for SHORT_FINAL stub convention"""
        s = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3,Period.MONTHS),
            stub_convention=StubConvention.SHORT_FINAL
        )

        s0 = SchedulePeriod(dt.date(2023,3,15),dt.date(2023,6,15),dt.date(2023,3,15),dt.date(2023,6,15))
        s1 = SchedulePeriod(dt.date(2023,6,15),dt.date(2023,9,15),dt.date(2023,6,15),dt.date(2023,9,15))
        s2 = SchedulePeriod(dt.date(2023,9,15),dt.date(2023,12,15),dt.date(2023,9,15),dt.date(2023,12,15))
        s3 = SchedulePeriod(dt.date(2023,12,15),dt.date(2024,1,1),dt.date(2023,12,15),dt.date(2024,1,2))

        print(s)

        self.assertEqual(
            s.get_period(0) == s0,
            True,
            "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(1) == s1,
            True,
            "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(2) == s2,
            True,
            "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(3) == s3,
            True,
            "Failed SHORT_FINAL stub unit test!"
        )


    def test_short_initial(self):
        """Unit test for SHORT_FINAL stub convention"""
        s = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3,Period.MONTHS),
            stub_convention=StubConvention.SHORT_INITIAL
        )

        print(s)

        s0 = SchedulePeriod(dt.date(2023,3,15),dt.date(2023,4,1),dt.date(2023,3,15),dt.date(2023,4,3))
        s1 = SchedulePeriod(dt.date(2023,4,1),dt.date(2023,7,1),dt.date(2023,4,3),dt.date(2023,7,3))
        s2 = SchedulePeriod(dt.date(2023,7,1),dt.date(2023,10,1),dt.date(2023,7,3),dt.date(2023,10,2))
        s3 = SchedulePeriod(dt.date(2023,10,1),dt.date(2024,1,1),dt.date(2023,10,2),dt.date(2024,1,2))

        self.assertEqual(
            s.get_period(0) == s0,
            True,
            "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(1) == s1,
            True,
            "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(2) == s2,
            True,
            "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(3) == s3,
            True,
            "Failed SHORT_INITIAL stub unit test!"
        )