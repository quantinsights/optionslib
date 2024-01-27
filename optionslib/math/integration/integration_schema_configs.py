"""Helper config dataclasses falling under IntegrationConfig umbrella.

Example use:
integrator = Integrator(
    default_config=RectangleConfig(steps=10_000)
    default_start=start,
    default_end=end,
)
"""

from typing import Union

from attrs import define, field, validators


@define
class RectangleConfig:
    """Config dataclass for rectangle integration."""
    steps: int = field(
        validator=validators.and_(validators.instance_of(int), validators.ge(0))
    )


@define
class MonteCarloConfig:
    """Config dataclass for Monte Carlo integration."""
    random_points: int = field(
        validator=validators.and_(validators.instance_of(int), validators.ge(0))
    )
    # TODO: add distribution to shuffle from


IntegrationConfig = Union[RectangleConfig, MonteCarloConfig]
