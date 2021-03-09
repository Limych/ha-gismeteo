# pylint: disable=protected-access,redefined-outer-name
"""Global fixtures for integration."""
# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.gismeteo import GismeteoApiClient

pytest_plugins = "pytest_homeassistant_custom_component"  # pylint: disable=invalid-name


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


@pytest.fixture
def gismeteo_api():
    """Make mock Gismeteo API client."""
    location_data = load_fixture("location.xml")
    forecast_data = load_fixture("forecast.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        return location_data if args[0].find("/cities/") >= 0 else forecast_data

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        yield
