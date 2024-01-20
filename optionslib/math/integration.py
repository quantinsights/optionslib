from enum import Enum, auto
from typing import Optional, Callable, Union

import numpy as np
from attrs import define

NumericType = Union[int, float, np.number]


class IntegrationSchema(Enum):
    RECTANGLE_RULE = auto()


def _rectangle_rule(
    integrand: Callable,
    start: NumericType,
    end: NumericType,
    steps: int,
) -> NumericType:
    x_points = np.linspace(start, end, steps)
    values = integrand(x_points)
    dx = (end - start) / np.float64(steps)
    return np.sum(values) * dx


@define(kw_only=True)
class Integrator:
    schema: IntegrationSchema
    default_start: Optional[NumericType] = None
    default_end: Optional[NumericType] = None
    default_step: Optional[int] = None

    __INTEGRATION_WORKER_MAP = {IntegrationSchema.RECTANGLE_RULE: _rectangle_rule}

    def __call__(
        self,
        integrand: Callable,
        *,
        start: Optional[NumericType] = None,
        end: Optional[NumericType] = None,
        steps: Optional[int] = None,
    ) -> float:
        """Calculates the integration value

        :param integrand: The integrated function
        :param start: The start of the integration interval
        :param end: The end of the integration interval
        :param steps: The number of steps to perform
        """
        start = start or self.default_start
        end = end or self.default_end
        steps = steps or self.default_step
        if start and end and steps:
            raise ValueError(
                "Integration not defined start=%s end=%s steps=%s" % (start, end, steps)
            )
        worker = self.__INTEGRATION_WORKER_MAP[self.schema]
        return worker(integrand, start, end, steps)


if __name__ == "__main__":
    integ = Integrator(
        schema=IntegrationSchema.RECTANGLE_RULE,
        default_start=0,
        default_end=np.pi,
        default_step=1000,
    )
    print(integ)
