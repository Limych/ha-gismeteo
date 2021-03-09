# pylint: disable=protected-access,redefined-outer-name
"""Test integration_blueprint config flow."""

from unittest.mock import patch

import pytest


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with patch(
        "custom_components.integration_blueprint.async_setup",
        return_value=True,
    ), patch(
        "custom_components.integration_blueprint.async_setup_entry",
        return_value=True,
    ):
        yield
