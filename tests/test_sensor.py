"""Tests for GisMeteo integration."""
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import assert_setup_component

from custom_components.gismeteo import DOMAIN


async def test_async_setup_platform(hass):
    """Test platform setup."""
    config = {SENSOR_DOMAIN: {"platform": DOMAIN}}
    with assert_setup_component(1, SENSOR_DOMAIN):
        assert await async_setup_component(hass, SENSOR_DOMAIN, config)
    await hass.async_block_till_done()
