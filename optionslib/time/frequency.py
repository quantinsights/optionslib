"""A module that supports periodic frequency in finance."""
import attrs
from attrs import define, field

from optionslib.types.enums import Period


@define
class Frequency:
    """Schedules are based on a periodic frequency. This determines how many
    periods are there in a year. For example, a periodic frequency of 3 months,
    results in 4 periods in a year.

    Frequency objects are initiated with:
    num_of_periods - an integer value
    units - One of [Days, Business days, Months, Years]
    """

    _num: int = field(alias="num", validator=attrs.validators.instance_of(int))
    _units: Period = field(
        alias="units", validator=attrs.validators.instance_of(Period)
    )

    @property
    def num(self):
        return self._num

    @property
    def units(self):
        return self._units

    def __repr__(self):
        return f"{self.num} {self.units.value}"
