"""Tests for GisMeteo integration."""

from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.gismeteo.const import DOMAIN


async def test_async_setup_platform(hass: HomeAssistant, gismeteo_api):
    """Test platform setup."""
    config = {
        WEATHER_DOMAIN: {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "Office",
        },
    }

    with assert_setup_component(1, WEATHER_DOMAIN):
        assert await async_setup_component(hass, WEATHER_DOMAIN, config)
    await hass.async_block_till_done()

    state = hass.states.get(f"{WEATHER_DOMAIN}.office")
    assert state is not None
    assert state.state == "snowy"
