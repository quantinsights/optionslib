"""
Module to support cashflow schedules.
"""
import numpy as np
import attrs
from attrs import define, field
import datetime as dt
from typing import List

from src.basics.enums import Period, BusinessDayConventions, RollConventions, StubConvention
from src.basics.holiday_calendar import HolidayCalendar, HolidayCalendarId
from src.basics.frequency import Frequency
from src.basics import utils


@define
class SchedulePeriod:
    """
    A period in a schedule.
    """

    _unadjusted_start_date : dt.date = field(
        validator=attrs.validators.instance_of(dt.date)
    )

    _unadjusted_end_date: dt.date = field(
        validator=attrs.validators.instance_of(dt.date)
    )

    _adjusted_start_date: dt.date = field(
        validator=attrs.validators.instance_of(dt.date)
    )

    _adjusted_end_date: dt.date = field(
        validator=attrs.validators.instance_of(dt.date)
    )

    @property
    def unadjusted_start_date(self) -> dt.date:
        """Returns the unadjusted period start date"""
        return self._unadjusted_start_date

    @property
    def unadjusted_end_date(self) -> dt.date:
        """Returns the unadjusted period end date"""
        return self._unadjusted_end_date

    @property
    def adjusted_start_date(self) -> dt.date:
        """Returns the adjusted period start date"""
        return self._adjusted_start_date

    @property
    def adjusted_end_date(self) -> dt.date:
        """Returns the adjusted period end date"""
        return self._adjusted_end_date

@define
class Schedule:
    """
    A complete schedule consisting of a list of `SchedulePeriods`.
    This typically forms the basis of financial calculations such as accrued interest.
    """
    # (unadjusted) start of the first schedule period
    _start_date : dt.date = field(validator=attrs.validators.instance_of(dt.date))

    # (unadjusted) end of the last schedule period
    _end_date : dt.date = field()

    # (unadjusted) start date of the first regular schedule period
    _first_regular_start_date : dt.date = field(default=None)

    # (unadjusted) end date of the last regular schedule period
    _last_regular_end_date : dt.date = field(default=None)

    _frequency : Frequency = field(
        default = Frequency(1, Period.YEARS),
        validator = attrs.validators.instance_of(Frequency)
    )

    _business_day_convention : BusinessDayConventions = field(
        default = BusinessDayConventions.MODIFIED_FOLLOWING,
        validator= attrs.validators.instance_of(BusinessDayConventions)
    )

    _roll_convention : RollConventions = field(default = None)

    _holiday_calendar : HolidayCalendar = field(
        default = HolidayCalendar(),
        validator = attrs.validators.instance_of(HolidayCalendar)
    )

    _stub_convention : StubConvention = field(
        default = StubConvention.SHORT_FINAL,
        validator = attrs.validators.instance_of(StubConvention)
    )

    _schedule_periods : List[SchedulePeriod] = field(default = [])

    @_end_date.validator
    def check_end_date(self, attribute, value) -> bool:
        if not isinstance(value, dt.date):
            raise ValueError("Invalid end date!")

        if value < self._start_date:
            raise ValueError(
                "The end date " + dt.date.strftime(value,"%Y-%m-%d") +
                " must be >= " +
                "the start date " + dt.date.strftime(self._start_date, "%Y-%m-%d")
            )

    @property
    def start_date(self) -> dt.date:
        """Returns the schedule start date"""
        return self._start_date

    @property
    def end_date(self) -> dt.date:
        """Returns the schedule end date"""
        return self._end_date

    @property
    def first_regular_start_date(self) -> dt.date:
        """Returns the first regular start date"""
        self.calculate_first_regular_start_date()

        return self._first_regular_start_date

    @property
    def last_regular_end_date(self) -> dt.date:
        """Returns the last regular end date"""
        self.calculate_last_regular_end_date()

        return self._last_regular_end_date

    @property
    def frequency(self) -> Frequency:
        """Returns the frequency"""
        return self._frequency

    @property
    def business_day_convention(self) -> BusinessDayConventions:
        """Returns the business date convention"""
        return self._business_day_convention

    @property
    def roll_convention(self) -> RollConventions:
        """Returns the roll convention"""
        if self._roll_convention is None:
            self.calculate_roll_convention()

        return self._roll_convention

    @property
    def holiday_calendar(self) -> HolidayCalendar:
        """Returns the holiday calendar"""
        return self._holiday_calendar

    @property
    def stub_convention(self) -> StubConvention:
        """Returns the stub convention"""
        return self._stub_convention

    @property
    def schedule_periods(self) -> List[SchedulePeriod]:
        """Returns the list of schedule periods"""
        if len(self._schedule_periods) == 0:
            self.build_schedule_periods()

        return self._schedule_periods

    def calculate_first_regular_start_date(self) -> None:
        """Calculates the first regular period start date"""

        def loop_back():
            date_i = self.end_date
            succ_date = None

            while date_i > self.start_date:
                succ_date = date_i
                date_i = utils.add_period(
                    date_i,
                    -1 * self.frequency.num,
                    self.frequency.units,
                    self.holiday_calendar
                )
            return succ_date

        if self.stub_convention == StubConvention.NONE or \
            self.stub_convention == StubConvention.SHORT_FINAL or \
            self.stub_convention == StubConvention.LONG_FINAL:
            calculated_first_regular_start_date = self.start_date

        if self.stub_convention == StubConvention.SHORT_INITIAL:
            calculated_first_regular_start_date = loop_back()

        if self.stub_convention == StubConvention.LONG_INITIAL:
            first_date = loop_back()
            calculated_first_regular_start_date = utils.add_period(
                first_date,
                self.frequency.num,
                self.frequency.units,
                self.holiday_calendar
            )

        if self._first_regular_start_date is None:
            self._first_regular_start_date = calculated_first_regular_start_date
        else:
            if self._first_regular_start_date != calculated_first_regular_start_date:
                raise ValueError("The first regular start date must be " +
                                 dt.date.strftime(calculated_first_regular_start_date,"%Y-%m-%d"))

    def calculate_last_regular_end_date(self) -> None:
        """Calculates the last regular period end date"""

        def loop_forward():
            date_i = self.start_date
            prev_date = None

            while date_i < self.end_date:
                prev_date = date_i
                date_i = utils.add_period(
                    date_i,
                    self.frequency.num,
                    self.frequency.units,
                    self.holiday_calendar
                )
            return prev_date

        if self.stub_convention == StubConvention.NONE or \
            self.stub_convention == StubConvention.SHORT_INITIAL or \
            self.stub_convention == StubConvention.LONG_INITIAL:
            calculated_last_regular_end_date = self.end_date

        if self.stub_convention == StubConvention.SHORT_FINAL:
            calculated_last_regular_end_date = loop_forward()

        if self.stub_convention == StubConvention.LONG_FINAL:
            last_date = loop_forward()
            calculated_last_regular_end_date = utils.add_period(
                last_date,
                -1 * self.frequency.num,
                self.frequency.units,
                self.holiday_calendar
            )

        if self._last_regular_end_date is None:
            self._last_regular_end_date = calculated_last_regular_end_date
        else:
            if self._last_regular_end_date != calculated_last_regular_end_date:
                raise ValueError("The last regular end date must be " +
                                 dt.date.strftime(calculated_last_regular_end_date,"%Y-%m-%d"))

    def calculate_roll_convention(self) -> None:
        """Deduces a roll convention"""

        if self.stub_convention == StubConvention.NONE:
            if self._start_date.day == self._end_date.day:
                self._roll_convention = RollConventions(self._start_date.day)
            else:
                raise ValueError(f"The end date must fall on {self.start_date.day} of the month!")

        if (self.stub_convention == StubConvention.SHORT_INITIAL or
                self.stub_convention == StubConvention.LONG_INITIAL):
            self._roll_convention = RollConventions(self._end_date.day)

        if (self.stub_convention == StubConvention.SHORT_FINAL or
                self.stub_convention == StubConvention.LONG_FINAL):
            self._roll_convention = RollConventions(self._start_date.day)

    def pre_validation(self):
        """Performs initial validation"""

        if not (self.end_date >= self.last_regular_end_date):
            raise ValueError("The end date" + dt.date.strftime(self.end_date,"%Y-%m-%d") +
                             " must be greater than or equal to the last regular date" +
                             dt.date.strftime(self.last_regular_end_date,"%Y-%m-%d") + "!")

        if not (self.last_regular_end_date >= self.first_regular_start_date):
            raise ValueError("The last regular period end date" +
                             dt.date.strftime(self.last_regular_end_date, "%Y-%m-%d") +
                             " must be greater than or equal to the first regular period start date" +
                             dt.date.strftime(self.first_regular_start_date, "%Y-%m-%d") + "!")

        if not (self.first_regular_start_date >= self.start_date):
            raise ValueError("The first regular period start date" +
                             dt.date.strftime(self.first_regular_start_date, "%Y-%m-%d") +
                             " must be greater than or equal to the schedule start date" +
                             dt.date.strftime(self.start_date, "%Y-%m-%d") + "!")

        if self.stub_convention == StubConvention.NONE:
            if not(self.start_date.day == self.roll_convention and
                   self.first_regular_start_date.day == self.roll_convention and
                   self.last_regular_end_date.day == self.roll_convention and
                   self.end_date.day == self.roll_convention
            ):
                raise ValueError("Failure - The schedule dates and roll convention are incompatible!")

        if (self.stub_convention == StubConvention.SHORT_INITIAL or
                self.stub_convention == StubConvention.LONG_INITIAL):
            if not(
                self.end_date.day == self.roll_convention and
                self.last_regular_end_date.day == self.roll_convention and
                self.first_regular_start_date.day == self.roll_convention
            ):
                raise ValueError("Failure - The schedule dates and roll convention are incompatible!")

        if (self.stub_convention == StubConvention.SHORT_FINAL or
                self.stub_convention == StubConvention.LONG_FINAL):
            if not(
                self.start_date.day == self.roll_convention and
                self.last_regular_end_date.day == self.roll_convention and
                self.first_regular_start_date.day == self.roll_convention
            ):
                raise ValueError("Failure - The schedule dates and roll convention are incompatible!")

    def build_short_final(self) -> None:
        """Builds schedule periods when stub convention is SHORT_FINAL"""

        if self.start_date != self.first_regular_start_date:
            current = self.start_date
        else:
            current = self.first_regular_start_date

        while current < self.last_regular_end_date:
            unadj_start = current
            unadj_end = utils.add_period(
                unadj_start,
                self.frequency.num,
                self.frequency.units,
                self.holiday_calendar
            )
            adj_start = utils.adjust(
                unadj_start,
                self.business_day_convention,
                self.holiday_calendar
            )
            adj_end = utils.adjust(
                unadj_end,
                self.business_day_convention,
                self.holiday_calendar
            )
            curr_period = SchedulePeriod(
                unadj_start, unadj_end, adj_start, adj_end
            )

            self._schedule_periods.append(curr_period)

            current = unadj_end

        adjusted_last_reg = utils.adjust(
            self.last_regular_end_date,
            self.business_day_convention,
            self.holiday_calendar
        )

        adjusted_end_date = utils.adjust(
            self.end_date,
            self.business_day_convention,
            self.holiday_calendar
        )

        last_period = SchedulePeriod(
            self.last_regular_end_date,
            self.end_date,
            adjusted_last_reg,
            adjusted_end_date
        )

        self._schedule_periods.append(last_period)

    def build_short_initial(self):
        """Builds schedule periods when stub convention is SHORT_INITIAL"""

        if self.end_date != self.last_regular_end_date:
            current = self.end_date
        else:
            current = self.last_regular_end_date

        while current > self.first_regular_start_date:
            unadj_end = current
            unadj_start = utils.add_period(
                unadj_end,
                -1 * self.frequency.num,
                self.frequency.units,
                self.holiday_calendar
            )
            adj_start = utils.adjust(
                unadj_start,
                self.business_day_convention,
                self.holiday_calendar
            )
            adj_end = utils.adjust(
                unadj_end,
                self.business_day_convention,
                self.holiday_calendar
            )
            curr_period = SchedulePeriod(
                unadj_start, unadj_end, adj_start, adj_end
            )

            self._schedule_periods.append(curr_period)

            current = unadj_start

        adjusted_first_reg = utils.adjust(
            self.first_regular_start_date,
            self.business_day_convention,
            self.holiday_calendar
        )

        adjusted_start_date = utils.adjust(
            self.start_date,
            self.business_day_convention,
            self.holiday_calendar
        )

        first_period = SchedulePeriod(
            self.start_date,
            self.first_regular_start_date,
            adjusted_start_date,
            adjusted_first_reg
        )

        self._schedule_periods.append(first_period)
        self._schedule_periods.reverse()


    def build_schedule_periods(self):
        """Build schedule periods"""

        # The schedule periods will be determined forwards from the regular
        # period start date. Any remaining period shorter than the standard
        # frequency will be allocated at the end.
        if self.stub_convention == StubConvention.SHORT_FINAL:
            self.build_short_final()

        # The schedule periods will be determined backwards from the last regular
        # period end date. Any remaining period shorter than the standard
        # frequency will be allocated at the start.
        if self.stub_convention == StubConvention.SHORT_INITIAL:
            self.build_short_initial()

    def build_schedule(self) -> None:
        """Build the schedule of cashflows"""

        self.calculate_roll_convention()
        self.calculate_first_regular_start_date()
        self.calculate_last_regular_end_date()
        self.pre_validation()

        self.build_schedule_periods()

    def get_period(self, i : int) -> SchedulePeriod:
        """Return the i-th schedule period"""

        return self.schedule_periods[i]

    def __repr__(self):
        """Pretty print the schedule"""
        s = ""
        s += "Start Date : " + dt.date.strftime(self.start_date,"%Y-%m-%d") + "\n"
        s += ("First regular period start date : " +
              dt.date.strftime(self.first_regular_start_date,"%Y-%m-%d") + "\n")
        s += ("Last regular period end date : " +
              dt.date.strftime(self.last_regular_end_date,"%Y-%m-%d") + "\n")
        s += "End Date : " + dt.date.strftime(self.end_date,"%Y-%m-%d") + "\n"
        s += "Frequency : " + self.frequency.__str__() + "\n"
        s += "Calendar : " + self.holiday_calendar.holiday_calendar_id.value + "\n"
        s += "Business day convention : " + self.business_day_convention.value + "\n"
        s += "Roll Convention : " + str(self.roll_convention.value) + "\n"
        s += "\n"
        s += "{} {:<21} {:<21} {:<21} {:<21}".format("Index",
                                                     "Unadjusted start date",
                                                     "Unadjusted end date",
                                                     "Adjusted start date",
                                                     "Adjusted end date") + "\n"
        s += ("----- "
              "--------------------- "
              "--------------------- "
              "--------------------- "
              "--------------------- ") + "\n"

        i = 1
        for p in self.schedule_periods:
            s += ("{}      "
                  " {:%Y-%m-%d}           "
                  " {:%Y-%m-%d}           "
                  " {:%Y-%m-%d}           "
                  " {:%Y-%m-%d}").format(
                i,
                p.unadjusted_start_date,
                p.unadjusted_end_date,
                p.adjusted_start_date,
                p.adjusted_end_date
            ) + "\n"
            i += 1
        return s
