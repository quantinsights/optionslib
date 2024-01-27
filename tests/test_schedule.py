"""Testing suite for schedules."""

import datetime as dt
import unittest

from optionslib.time.frequency import Frequency
from optionslib.time.schedule import Schedule, SchedulePeriod
from optionslib.types.enums import Period, StubConvention


class TestSchedule(unittest.TestCase):
    """Unit tests for Schedule, SchedulePeriod."""

    def __test_schedule_periods(
        self, schedule: Schedule, expected_periods: list[SchedulePeriod]
    ):
        """Unit test helper."""
        print(schedule)
        for count, expected_period in enumerate(expected_periods):
            self.assertEqual(
                schedule.get_period(count),
                expected_period,
                msg=f"Failed SHORT_INITIAL stub unit test number {count}.",
            )

    def test_short_final(self):
        """Unit test for SHORT_FINAL stub convention."""
        schedule = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.SHORT_FINAL,
        )

        expected_periods = [
            SchedulePeriod(
                dt.date(2023, 3, 15),
                dt.date(2023, 6, 15),
                dt.date(2023, 3, 15),
                dt.date(2023, 6, 15),
            ),
            SchedulePeriod(
                dt.date(2023, 6, 15),
                dt.date(2023, 9, 15),
                dt.date(2023, 6, 15),
                dt.date(2023, 9, 15),
            ),
            SchedulePeriod(
                dt.date(2023, 9, 15),
                dt.date(2023, 12, 15),
                dt.date(2023, 9, 15),
                dt.date(2023, 12, 15),
            ),
            SchedulePeriod(
                dt.date(2023, 12, 15),
                dt.date(2024, 1, 1),
                dt.date(2023, 12, 15),
                dt.date(2024, 1, 2),
            ),
        ]
        self.__test_schedule_periods(schedule, expected_periods)

    def test_short_initial(self):
        """Unit test for SHORT_INITIAL stub convention."""
        schedule = Schedule(
            start_date=dt.date(2023, 3, 15),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.SHORT_INITIAL,
        )

        expected_periods = [
            SchedulePeriod(
                dt.date(2023, 3, 15),
                dt.date(2023, 4, 1),
                dt.date(2023, 3, 15),
                dt.date(2023, 4, 3),
            ),
            SchedulePeriod(
                dt.date(2023, 4, 1),
                dt.date(2023, 7, 1),
                dt.date(2023, 4, 3),
                dt.date(2023, 7, 3),
            ),
            SchedulePeriod(
                dt.date(2023, 7, 1),
                dt.date(2023, 10, 1),
                dt.date(2023, 7, 3),
                dt.date(2023, 10, 2),
            ),
            SchedulePeriod(
                dt.date(2023, 10, 1),
                dt.date(2024, 1, 1),
                dt.date(2023, 10, 2),
                dt.date(2024, 1, 2),
            ),
        ]
        self.__test_schedule_periods(schedule, expected_periods)

    def test_both(self):
        """Unit test for StubConvention.BOTH."""
        schedule = Schedule(
            start_date=dt.date(2023, 3, 15),
            first_regular_start_date=dt.date(2023, 3, 20),
            last_regular_end_date=dt.date(2023, 12, 20),
            end_date=dt.date(2024, 1, 1),
            frequency=Frequency(3, Period.MONTHS),
            stub_convention=StubConvention.BOTH,
        )

        expected_periods = [
            SchedulePeriod(
                dt.date(2023, 3, 15),
                dt.date(2023, 3, 20),
                dt.date(2023, 3, 15),
                dt.date(2023, 3, 20),
            ),
            SchedulePeriod(
                dt.date(2023, 3, 20),
                dt.date(2023, 6, 20),
                dt.date(2023, 3, 20),
                dt.date(2023, 6, 20),
            ),
            SchedulePeriod(
                dt.date(2023, 6, 20),
                dt.date(2023, 9, 20),
                dt.date(2023, 6, 20),
                dt.date(2023, 9, 20),
            ),
            SchedulePeriod(
                dt.date(2023, 9, 20),
                dt.date(2023, 12, 20),
                dt.date(2023, 9, 20),
                dt.date(2023, 12, 20),
            ),
            SchedulePeriod(
                dt.date(2023, 12, 20),
                dt.date(2024, 1, 1),
                dt.date(2023, 12, 20),
                dt.date(2024, 1, 2),
            ),
        ]
        self.__test_schedule_periods(schedule, expected_periods)

    def test_day29_roll_convention(self):
        """Unit test for day 29 roll convention."""

        schedule = Schedule(
            start_date=dt.date(2023, 1, 1),
            first_regular_start_date=dt.date(2023, 1, 29),
            last_regular_end_date=dt.date(2023, 3, 29),
            end_date=dt.date(2023, 4, 1),
            frequency=Frequency(1, Period.MONTHS),
            stub_convention=StubConvention.BOTH,
        )

        expected_periods = [
            SchedulePeriod(
                dt.date(2023, 1, 1),
                dt.date(2023, 1, 29),
                dt.date(2023, 1, 3),
                dt.date(2023, 1, 30),
            ),
            SchedulePeriod(
                dt.date(2023, 1, 29),
                dt.date(2023, 2, 28),
                dt.date(2023, 1, 30),
                dt.date(2023, 2, 28),
            ),
            SchedulePeriod(
                dt.date(2023, 2, 28),
                dt.date(2023, 3, 29),
                dt.date(2023, 2, 28),
                dt.date(2023, 3, 29),
            ),
            SchedulePeriod(
                dt.date(2023, 3, 29),
                dt.date(2023, 4, 1),
                dt.date(2023, 3, 29),
                dt.date(2023, 4, 3),
            ),
        ]
        self.__test_schedule_periods(schedule, expected_periods)
