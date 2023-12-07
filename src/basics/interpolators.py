"""Interpolator objects.

Interpolator objects are initiated with:
    x_values - sorted list of numeric values (int, float, np.number)
    y_values - list of numeric values
    extrapolate - boolean if object should return value if call is outside range.

Example usage:
    x_values = [1, 2, 4, ]
    y_values = [2, 8, 4.5, ]
    interpolator = LinearInterpolator(
        x_values,
        y_values,
        extrapolate=True
    )
    print([interpolator(x) for x in range(8)])
        >>[2.0, 2.0, 8.0, 6.25, 4.5, 4.5, 4.5, 4.5]

Base abstract class:
    Interpolator
Concrete implementations:
    LinearInterpolator
"""

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List, Union, cast

import datetime as dt
import numpy as np
from attrs import define, field

NumericType = Union[int, float, np.number]


class ExtrapolateIndex(IntEnum):
    """Helper extrapolations enum.

    Indicates if we are in front of or in the back of the interpolation
    range.
    """

    FRONT = -1
    BACK = -2


@define(slots=False)
class Interpolator(ABC):
    """Abstract base class for interpolator objects."""

    _xs: List[NumericType] | List[dt.datetime] | np.ndarray = field(alias="x_values")
    _ys: List[NumericType] | np.ndarray = field(alias="y_values")
    _extrapolate: bool = field(
        alias="extrapolate",
        default=False,
    )

    @_xs.validator
    def check_x_values(self, attribute, values):  # pylint: disable=W0613
        """Validates that x_values are sorted."""
        if not values:
            raise ValueError("list of x values is empty.")
        if len(values) == 1:
            return
        zero_point = dt.timedelta(0) if isinstance(values[0], dt.date) else 0
        for i in range(len(values) - 1):
            if values[i + 1] - values[i] < zero_point:
                raise ValueError("List of x values is not sorted")

    @_ys.validator
    def check_y_values(self, attribute, values):  # pylint: disable=W0613
        """Validates that y_values equal length to x_values."""
        if len(values) != len(self._xs):
            raise ValueError("List of y values is different len from x values.")

    @property
    def x_values(self) -> List[float]:
        """Get x values."""
        return self._xs

    @property
    def y_values(self) -> List[float]:
        """Get y values."""
        return [float(x) for x in self._ys]

    @property
    def is_extrapolator(self) -> bool:
        """Check if object extrapolates."""
        return self._extrapolate

    @abstractmethod
    def __call__(self, x: float | dt.date) -> float:
        """Call to get interpolated y value."""

    def __len__(self):
        """Get length of interpolator."""
        # unambiguous since we validated equal len
        return len(self._xs)


class LinearInterpolator(Interpolator):
    """Interpolator using linear interpolation, constant extrapolation."""

    def __call__(self, x: float | dt.date) -> float:
        """Call to get interpolated y value."""
        index = self.__find_index(x)

        # negative index mean outside range
        if index < 0 and not self.is_extrapolator:
            raise ValueError(
                "Given range outside of interpolated range to non-extrapolator."
            )
        match index:
            case ExtrapolateIndex.FRONT:
                result = self._ys[0]
            case ExtrapolateIndex.BACK:
                result = self._ys[-1]
            case _:
                x_delta = self.__convert_to_float(self._xs[index + 1] - self._xs[index])
                y_delta = self._ys[index + 1] - self._ys[index]
                slope = y_delta / x_delta
                result = self._ys[index] + self.__convert_to_float(x - self._xs[index]) * slope
        # enforce float -> flot signature of interpolator
        return float(result)

    def __find_index(self, x: float) -> int:
        """Helper function to get the adjacent index."""
        if x < self._xs[0]:
            return ExtrapolateIndex.FRONT
        for i in range(len(self) - 1):
            if self._xs[i] <= x < self._xs[i + 1]:
                return i
        return ExtrapolateIndex.BACK

    @staticmethod
    def __convert_to_float(delta: float | dt.timedelta ) -> float:
        """Convert the potential time delta to year fraction float."""
        if isinstance(delta, dt.timedelta):
            # convert to year fraction, assume daily granularity
            delta = delta.days / 365
        return cast(float, delta)
