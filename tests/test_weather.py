"""Tests for GisMeteo integration."""
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.gismeteo import DOMAIN


async def test_async_setup_platform(hass):
    """Test platform setup."""
    config = {WEATHER_DOMAIN: {"platform": DOMAIN}}
    with assert_setup_component(1, WEATHER_DOMAIN):
        assert await async_setup_component(hass, WEATHER_DOMAIN, config)
    await hass.async_block_till_done()
