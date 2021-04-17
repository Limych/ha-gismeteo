# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""

from asynctest import Mock
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import ATTRIBUTION
from custom_components.gismeteo.weather import GismeteoWeather


async def test_entity_initialization(hass: HomeAssistant):
    """Test entity initialization."""
    mock_api = Mock()
    mock_api.unique_id = "qwe"
    mock_api.condition = Mock(return_value="asd")
    mock_api.attributes = {}

    coordinator = GismeteoDataUpdateCoordinator(hass, mock_api)
    entity = GismeteoWeather("Test", coordinator)

    assert entity.unique_id == "qwe"
    assert entity.name == "Test"
    assert entity.attribution == ATTRIBUTION
    assert entity.condition == "asd"
    assert entity.temperature_unit == TEMP_CELSIUS
