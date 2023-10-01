"""Tests for GisMeteo integration."""
from unittest.mock import Mock

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import (
    ATTR_LAT,
    ATTR_LON,
    ATTRIBUTION,
    DOMAIN,
    NAME,
)
from custom_components.gismeteo.entity import GismeteoEntity
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_ID,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    CONF_SHOW_ON_MAP,
)
from homeassistant.core import HomeAssistant

from tests.const import (
    MOCK_API_ID,
    MOCK_CONFIG,
    MOCK_LATITUDE,
    MOCK_LONGITUDE,
    MOCK_UNIQUE_ID,
)


async def test_entity_initialization(hass: HomeAssistant):
    """Test sensor initialization."""
    mock_api = Mock()
    mock_api.condition = Mock(return_value="asd")
    mock_api.attributes = {
        ATTR_ID: MOCK_API_ID,
    }
    mock_api.latitude = MOCK_LATITUDE
    mock_api.longitude = MOCK_LONGITUDE

    coordinator = GismeteoDataUpdateCoordinator(hass, MOCK_UNIQUE_ID, mock_api)
    entity = GismeteoEntity("Test", coordinator, MOCK_CONFIG)

    expected_device_info = {
        "identifiers": {(DOMAIN, MOCK_API_ID)},
        "name": NAME,
        "manufacturer": NAME,
        "model": "Forecast",
    }
    expected_attributes = {
        ATTR_ID: MOCK_API_ID,
        ATTR_LAT: MOCK_LATITUDE,
        ATTR_LON: MOCK_LONGITUDE,
        ATTR_ATTRIBUTION: ATTRIBUTION,
    }

    assert entity.device_info == expected_device_info
    assert entity.extra_state_attributes == expected_attributes

    config = MOCK_CONFIG.copy()
    config[CONF_SHOW_ON_MAP] = True
    entity = GismeteoEntity("Test", coordinator, config)

    expected_attributes.pop(ATTR_LAT)
    expected_attributes.pop(ATTR_LON)
    expected_attributes.update(
        {
            ATTR_LATITUDE: MOCK_LATITUDE,
            ATTR_LONGITUDE: MOCK_LONGITUDE,
        }
    )

    assert entity.device_info == expected_device_info
    assert entity.extra_state_attributes == expected_attributes
