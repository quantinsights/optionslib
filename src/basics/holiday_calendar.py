"""
This module provides functionality to working with holiday calendars.
"""
from typing import List
import attr
import datetime as dt

import numpy as np

from src.basics.enums import HolidayCalendarId, DayOfWeek
from src.basics import utils

@attr.s
class HolidayCalendar:
    """
    In many calculations in financial mathematics, we are interested to know if a given date
    is a business date or not. This class is implements a few standard calendars.
    """
    __first_weekend_day = attr.ib(default=DayOfWeek.SATURDAY,
                                  validator=attr.validators.instance_of(DayOfWeek))

    __second_weekend_day = attr.ib(default=DayOfWeek.SUNDAY,
                                   validator=attr.validators.instance_of(DayOfWeek))

    __holiday_calendar_id = attr.ib(default=HolidayCalendarId.LONDON,
                                    validator=attr.validators.instance_of(HolidayCalendarId))

    def __attrs_post_init__(self):
        self.__holiday_dates : List[dt.date] = None

    @property
    def first_weekend_day(self):
        """Return the first weekend day"""
        return self.__first_weekend_day

    @property
    def second_weekend_day(self):
        """Return the second weekend day"""
        return self.__second_weekend_day

    @property
    def holiday_calendar_id(self):
        """Return the holiday calendar id"""
        return self.__holiday_calendar_id

    @property
    def holiday_dates(self):
        """Return the holiday dates"""
        if self.__holiday_dates is None:
            self.generate_calendar()

        return self.__holiday_dates

    def generate_calendar(self) -> None:
        """
        Generates the holiday calendar
        Reference. https://github.com/OpenGamma/Strata/blob/main/modules/basics/src/main/java/com/opengamma/strata/basics/date/GlobalHolidayCalendars.java
        """
        if self.holiday_calendar_id == HolidayCalendarId.LONDON:
            self.generate_london_calendar()

    def generate_london_calendar(self) -> None:
        """
        Algorithm for the London holiday calendar dates
        """
        holidays = []

        for year in range(1950,2101,1):
            # new year
            if year >= 1974:
                holidays.append(utils.bump_to_mon(dt.date(year,1,1)))

            # easter
            holidays.append(utils.easter(year) - dt.timedelta(days=2))
            holidays.append(utils.easter(year) + dt.timedelta(days=1))

            # early may
            if year == 1995 or year == 2020:
                holidays.append(dt.date(year, 5, 8))
            else:
                if year >= 1978:
                    holidays.append(utils.first_in_month(year, 5, DayOfWeek.MONDAY))

            # spring
            if year == 2002:
                # golden jubilee
                holidays.append(dt.date(2002, 6, 3))
                holidays.append(dt.date(2002, 6, 4))
            elif year == 2012:
                # diamond jubilee
                holidays.append(dt.date(2012, 6, 4))
                holidays.append(dt.date(2012, 6, 5))
            elif year == 2022:
                # platinum jubilee
                holidays.append(dt.date(2022, 6, 2))
                holidays.append(dt.date(2022, 6, 3))
            elif year == 1967 or year == 1970:
                holidays.append(utils.last_in_month(year, 5, DayOfWeek.MONDAY))
            elif year < 1971:
                # White sunday
                holidays.append(utils.easter(year) + dt.timedelta(days=50))
            else:
                holidays.append(utils.last_in_month(year, 5, DayOfWeek.MONDAY))

            # summer
            if year < 1965:
                holidays.append(utils.first_in_month(year, 8, DayOfWeek.MONDAY))
            elif year < 1971:
                holidays.append(utils.last_in_month(year, 8, DayOfWeek.SATURDAY) + dt.timedelta(days=2))
            else:
                holidays.append(utils.last_in_month(year, 8, DayOfWeek.MONDAY))

            # queen's funeral
            if year == 2022:
                holidays.append(dt.date(2022, 9, 19))

            # Christmas
            holidays.append(utils.christmas_bumped_sun(year))
            holidays.append(utils.boxing_day_bumped_sat_sun(year))

        holidays.append(dt.date(1999, 12, 31)) # millenium
        holidays.append(dt.date(2011, 4, 29)) # royal wedding
        holidays.append(dt.date(2023, 5, 8)) # king's coronation

        holidays = self.remove_sat_sun(holidays)
        self.__holiday_dates = holidays

    def remove_sat_sun(self, holidays : List[dt.date]) -> List[dt.date]:
        """
        Removes the first weekend day and second weekend day from the list of holidays
        """
        return list(
            filter(
                lambda x : x.weekday() != self.first_weekend_day and x.weekday() != self.second_weekend_day,
                holidays
            )
        )

    def is_holiday(self, d:dt.date) -> bool:
        """
        Tests if a given date is a holiday.
        """
        if d.weekday() == self.first_weekend_day or \
            d.weekday() == self.second_weekend_day:
            return True

        if d in self.holiday_dates:
            return True

        return False

    def is_bus_day(self, d:dt.date) -> bool:
        """
        Tests if a given date is a business date
        """
        return not(self.is_holiday(d))

if __name__ == "__main__":
    calendar = HolidayCalendar(
        DayOfWeek.SATURDAY,
        DayOfWeek.SUNDAY,
        HolidayCalendarId.LONDON
    )

    assert (calendar.is_holiday(dt.date(2023,12,9)) is True)
    assert (calendar.is_holiday(dt.date(2023,12,11)) is False)
    assert (calendar.is_holiday(dt.date(2023, 12, 26)) is True)