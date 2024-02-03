"""Implementations of the integration schema."""

from typing import Callable

import numpy as np

from optionslib.math.integration.integration_schema_configs import (
    IntegrationConfig,
    MonteCarloConfig,
    RectangleConfig,
)
from optionslib.types.var_types import NumericType

IntegrationSchema = Callable[
    [Callable, NumericType, NumericType, IntegrationConfig], NumericType
]


def rectangle_rule(
    integrand: Callable,
    start: NumericType,
    end: NumericType,
    config: RectangleConfig,
) -> NumericType:
    """
    Implementation of the rectangle rule for integration.

    Args:
        integrand: function to integrate
        start: start of integration interval
        end: end of integration interval
        config: integration configuration

    """
    steps = config.steps
    x_points = np.linspace(start, end, steps)
    values = integrand(x_points)
    dx = (end - start) / np.float64(steps)
    return np.sum(values) * dx


def monte_carlo(
    integrand: Callable,
    start: NumericType,
    end: NumericType,
    config: MonteCarloConfig,
) -> NumericType:
    """
    Implementation of the monte carlo schema for integration.

    Args:
        integrand: function to integrate
        start: start of integration interval
        end: end of integration interval
        config: integration configuration

    """
    random_points = config.random_points
    x_points = np.random.uniform(start, end, random_points)
    values = integrand(x_points)
    average_dx = (end - start) / np.float64(random_points)
    return np.sum(values) * average_dx
