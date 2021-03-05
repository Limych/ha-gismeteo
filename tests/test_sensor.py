"""Tests for GisMeteo integration."""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.gismeteo.const import CONF_FORECAST, DOMAIN, SENSOR_TYPES


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

    state = hass.states.get(f"{SENSOR_DOMAIN}.office_forecast")
    assert state is not None
    assert state.state == "clear-night"
