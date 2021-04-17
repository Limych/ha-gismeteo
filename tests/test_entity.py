# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""

from asynctest import Mock
from homeassistant.const import ATTR_ID
from homeassistant.core import HomeAssistant

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import DOMAIN, NAME
from custom_components.gismeteo.entity import GismeteoEntity


async def test_entity_initialization(hass: HomeAssistant):
    """Test entity initialization."""
    mock_api = Mock()
    mock_api.unique_id = "qwe"
    mock_api.attributes = {ATTR_ID: "asd"}

    coordinator = GismeteoDataUpdateCoordinator(hass, mock_api)
    entity = GismeteoEntity("Test", coordinator)

    assert entity._gismeteo is mock_api
    assert entity.device_info == {
        "identifiers": {(DOMAIN, "asd")},
        "name": NAME,
        "manufacturer": NAME,
        "model": "Forecast",
    }
