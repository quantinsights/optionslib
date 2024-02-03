"""
Entrypoint module for integration functionalities.

Import from here and not directly.

"""

from optionslib.math.integration.integration_schema_configs import (
    IntegrationConfig,
    MonteCarloConfig,
    RectangleConfig,
)
from optionslib.math.integration.integrator import Integrator
