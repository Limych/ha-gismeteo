"""Tests for GisMeteo integration."""
from unittest.mock import patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowManager
from homeassistant.setup import async_setup_component

from custom_components.gismeteo.const import DOMAIN


async def test_async_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    config = {
        SENSOR_DOMAIN: {
            CONF_PLATFORM: DOMAIN,
        },
    }

    with patch.object(FlowManager, "async_init") as flow_init:
        assert await async_setup_component(hass, SENSOR_DOMAIN, config)
        await hass.async_block_till_done()

        assert flow_init.called
