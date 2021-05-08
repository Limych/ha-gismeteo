"""Tests for GisMeteo integration."""

from asynctest import Mock
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_PLATFORM,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import (
    ATTRIBUTION,
    CONF_FORECAST,
    DOMAIN,
    SENSOR_TYPES,
)
from custom_components.gismeteo.sensor import GismeteoSensor, fix_kinds

from tests.const import MOCK_UNIQUE_ID


async def test_fix_kinds(caplog):
    """Test fix_kinds function."""
    caplog.clear()
    res = fix_kinds([])
    assert res == []
    assert len(caplog.records) == 0

    caplog.clear()
    res = fix_kinds(["qwe", "asd"])
    assert res == ["asd", "qwe"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = fix_kinds(["qwe", "asd", "pressure", "forecast", "pressure_mmhg"])
    assert res == ["asd", "pressure", "qwe"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = fix_kinds(["qwe", "asd", "weather"])
    assert res == ["asd", "condition", "qwe"]
    assert len(caplog.records) == 1

    caplog.clear()
    res = fix_kinds(["qwe", "asd", "weather"], False)
    assert res == ["asd", "condition", "qwe"]
    assert len(caplog.records) == 0


async def test_sensor_initialization(hass: HomeAssistant):
    """Test sensor initialization."""
    mock_api = Mock()
    mock_api.condition = Mock(return_value="asd")
    mock_api.attributes = {}

    coordinator = GismeteoDataUpdateCoordinator(hass, MOCK_UNIQUE_ID, mock_api)
    sensor = GismeteoSensor("Test", "condition", coordinator)

    expected_attributes = {
        ATTR_ATTRIBUTION: ATTRIBUTION,
    }

    assert sensor.name == "Test Condition"
    assert sensor.unique_id == f"{MOCK_UNIQUE_ID}-condition"
    assert sensor.should_poll is False
    assert sensor.available is True
    assert sensor.state == "asd"
    assert sensor.unit_of_measurement is None
    assert sensor.icon is None
    assert sensor.device_state_attributes == expected_attributes


async def test_async_setup_platform(hass: HomeAssistant, gismeteo_api):
    """Test platform setup."""
    config = {
        SENSOR_DOMAIN: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "Office",
            CONF_MONITORED_CONDITIONS: list(SENSOR_TYPES.keys()),
            CONF_FORECAST: True,
        },
    }

    with assert_setup_component(1, SENSOR_DOMAIN):
        assert await async_setup_component(hass, SENSOR_DOMAIN, config)
    await hass.async_block_till_done()

    state = hass.states.get(f"{SENSOR_DOMAIN}.office_condition")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR_DOMAIN}.office_3h_forecast")
    assert state is not None
    assert state.state == "clear-night"
