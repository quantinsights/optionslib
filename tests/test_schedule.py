import datetime as dt
import unittest

from optionslib.time.enums import Period, StubConvention
from optionslib.time.frequency import Frequency
from optionslib.time.schedule import Schedule, SchedulePeriod


class TestSchedule(unittest.TestCase):
    """Unit tests for Schedule"""

    def test_short_final(self):
        """Unit test for SHORT_FINAL stub convention"""
        s = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.SHORT_FINAL,
        )

        s0 = SchedulePeriod(
            dt.date(2023, 3, 15),
            dt.date(2023, 6, 15),
            dt.date(2023, 3, 15),
            dt.date(2023, 6, 15),
        )
        s1 = SchedulePeriod(
            dt.date(2023, 6, 15),
            dt.date(2023, 9, 15),
            dt.date(2023, 6, 15),
            dt.date(2023, 9, 15),
        )
        s2 = SchedulePeriod(
            dt.date(2023, 9, 15),
            dt.date(2023, 12, 15),
            dt.date(2023, 9, 15),
            dt.date(2023, 12, 15),
        )
        s3 = SchedulePeriod(
            dt.date(2023, 12, 15),
            dt.date(2024, 1, 1),
            dt.date(2023, 12, 15),
            dt.date(2024, 1, 2),
        )

        print(s)

        self.assertEqual(
            s.get_period(0) == s0, True, "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(1) == s1, True, "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(2) == s2, True, "Failed SHORT_FINAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(3) == s3, True, "Failed SHORT_FINAL stub unit test!"
        )

        del s

    def test_short_initial(self):
        """Unit test for SHORT_INITIAL stub convention"""
        s = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.SHORT_INITIAL,
        )

        print(s)

        s0 = SchedulePeriod(
            dt.date(2023, 3, 15),
            dt.date(2023, 4, 1),
            dt.date(2023, 3, 15),
            dt.date(2023, 4, 3),
        )
        s1 = SchedulePeriod(
            dt.date(2023, 4, 1),
            dt.date(2023, 7, 1),
            dt.date(2023, 4, 3),
            dt.date(2023, 7, 3),
        )
        s2 = SchedulePeriod(
            dt.date(2023, 7, 1),
            dt.date(2023, 10, 1),
            dt.date(2023, 7, 3),
            dt.date(2023, 10, 2),
        )
        s3 = SchedulePeriod(
            dt.date(2023, 10, 1),
            dt.date(2024, 1, 1),
            dt.date(2023, 10, 2),
            dt.date(2024, 1, 2),
        )

        self.assertEqual(
            s.get_period(0) == s0, True, "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(1) == s1, True, "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(2) == s2, True, "Failed SHORT_INITIAL stub unit test!"
        )

        self.assertEqual(
            s.get_period(3) == s3, True, "Failed SHORT_INITIAL stub unit test!"
        )

        del s

    def test_both(self):
        """Unit test for StubConvention.BOTH"""
        s = Schedule(
            start_date=dt.date(2023, 3, 15),
            first_regular_start_date=dt.date(2023, 3, 20),
            last_regular_end_date=dt.date(2023, 12, 20),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.BOTH,
        )

        print(s)

        s0 = SchedulePeriod(
            dt.date(2023, 3, 15),
            dt.date(2023, 3, 20),
            dt.date(2023, 3, 15),
            dt.date(2023, 3, 20),
        )
        s1 = SchedulePeriod(
            dt.date(2023, 3, 20),
            dt.date(2023, 6, 20),
            dt.date(2023, 3, 20),
            dt.date(2023, 6, 20),
        )
        s2 = SchedulePeriod(
            dt.date(2023, 6, 20),
            dt.date(2023, 9, 20),
            dt.date(2023, 6, 20),
            dt.date(2023, 9, 20),
        )
        s3 = SchedulePeriod(
            dt.date(2023, 9, 20),
            dt.date(2023, 12, 20),
            dt.date(2023, 9, 20),
            dt.date(2023, 12, 20),
        )
        s4 = SchedulePeriod(
            dt.date(2023, 12, 20),
            dt.date(2024, 1, 1),
            dt.date(2023, 12, 20),
            dt.date(2024, 1, 2),
        )

        self.assertEqual(s.get_period(0) == s0, True, "Failed BOTH stub unit test!")

        self.assertEqual(s.get_period(1) == s1, True, "Failed BOTH stub unit test!")

        self.assertEqual(s.get_period(2) == s2, True, "Failed BOTH stub unit test!")

        self.assertEqual(s.get_period(3) == s3, True, "Failed BOTH stub unit test!")

        self.assertEqual(s.get_period(4) == s4, True, "Failed BOTH stub unit test!")

        del s

    def test_day29_roll_convention(self):
        """Unit test for day 29 roll convention"""

        s = Schedule(
            start_date=dt.date(2023, 1, 1),
            first_regular_start_date=dt.date(2023, 1, 29),
            last_regular_end_date=dt.date(2023, 3, 29),
            end_date=dt.date(2023, 4, 1),
            frequency=Frequency(1, Period.MONTHS),
            stub_convention=StubConvention.BOTH,
        )

        print(s)

        s0 = SchedulePeriod(
            dt.date(2023, 1, 1),
            dt.date(2023, 1, 29),
            dt.date(2023, 1, 3),
            dt.date(2023, 1, 30),
        )
        s1 = SchedulePeriod(
            dt.date(2023, 1, 29),
            dt.date(2023, 2, 28),
            dt.date(2023, 1, 30),
            dt.date(2023, 2, 28),
        )
        s2 = SchedulePeriod(
            dt.date(2023, 2, 28),
            dt.date(2023, 3, 29),
            dt.date(2023, 2, 28),
            dt.date(2023, 3, 29),
        )
        s3 = SchedulePeriod(
            dt.date(2023, 3, 29),
            dt.date(2023, 4, 1),
            dt.date(2023, 3, 29),
            dt.date(2023, 4, 3),
        )

        self.assertEqual(
            s.get_period(0) == s0, True, "Failed RollConvention.DAY_29 stub unit test!"
        )

        self.assertEqual(
            s.get_period(1) == s1, True, "Failed RollConvention.DAY_29 stub unit test!"
        )

        self.assertEqual(
            s.get_period(2) == s2, True, "Failed RollConvention.DAY_29 stub unit test!"
        )

        self.assertEqual(
            s.get_period(3) == s3, True, "Failed RollConvention.DAY_29 stub unit test!"
        )

        del s
