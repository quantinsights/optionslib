"""
This module provides functionality to working with holiday calendars.
"""
import datetime as dt
from typing import List

import attrs
from attrs import define, field

from optionslib.time import utils
from optionslib.time.enums import DayOfWeek, HolidayCalendarId


@define
class HolidayCalendar:
    """
    In many calculations in financial mathematics, we are interested to know if a given date
    is a business date or not. This class implements a few standard calendars.
    """

    __first_weekend_day = field(
        default=DayOfWeek.SATURDAY, validator=attrs.validators.instance_of(DayOfWeek)
    )

    __second_weekend_day = field(
        default=DayOfWeek.SUNDAY, validator=attrs.validators.instance_of(DayOfWeek)
    )

    __holiday_calendar_id = field(
        default=HolidayCalendarId.LONDON,
        validator=attrs.validators.instance_of(HolidayCalendarId),
    )

    __holiday_dates = field(default=None)

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
        Algorithm for the London holiday calendar dates.
        Reference. https://www.gov.uk/bank-holidays
        """
        holidays = []

        for year in range(1950, 2101, 1):
            # new year
            if year >= 1974:
                holidays.append(utils.bump_to_mon(dt.date(year, 1, 1)))

            # easter
            holidays.append(utils.easter(year) - dt.timedelta(days=2))
            holidays.append(utils.easter(year) + dt.timedelta(days=1))

            # early may
            if year in [1995, 2020]:
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
            elif year in [1967, 1970]:
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
                holidays.append(
                    utils.last_in_month(year, 8, DayOfWeek.SATURDAY)
                    + dt.timedelta(days=2)
                )
            else:
                holidays.append(utils.last_in_month(year, 8, DayOfWeek.MONDAY))

            # queen's funeral
            if year == 2022:
                holidays.append(dt.date(2022, 9, 19))

            # Christmas
            holidays.append(utils.christmas_bumped_sat_or_sun(year))
            holidays.append(utils.boxing_day_bumped_sat_sun(year))

        holidays.append(dt.date(1999, 12, 31))  # millenium
        holidays.append(dt.date(2011, 4, 29))  # royal wedding
        holidays.append(dt.date(2023, 5, 8))  # king's coronation

        holidays = self.remove_sat_sun(holidays)
        self.__holiday_dates = holidays

    def remove_sat_sun(self, holidays: List[dt.date]) -> List[dt.date]:
        """
        Removes the first weekend day and second weekend day from the list of holidays.
        """
        return list(
            filter(
                lambda x: x.weekday() != self.first_weekend_day
                and x.weekday() != self.second_weekend_day,
                holidays,
            )
        )

    def is_holiday(self, date_value: dt.date) -> bool:
        """
        Tests if a given date is a holiday.
        """
        if (
            date_value.weekday() == self.first_weekend_day
            or date_value.weekday() == self.second_weekend_day
        ):
            return True

        if date_value in self.holiday_dates:
            return True

        return False

    def is_bus_day(self, date_value: dt.date) -> bool:
        """
        Tests if a given date is a business date
        """
        return not self.is_holiday(date_value)
