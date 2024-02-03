"""Commonly used types."""

import datetime as dt
from typing import Dict, Union

import numpy as np

NumericType = Union[int, float, np.number]
VolSurfaceDataType = Dict[dt.date, float]
