"""Tests for GisMeteo integration."""
from unittest.mock import patch

import pytest
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowManager
from homeassistant.setup import async_setup_component

from custom_components.gismeteo.const import DOMAIN


@pytest.mark.parametrize("load_registries", [False])
async def test_async_setup_platform(hass: HomeAssistant):
    """Test platform setup."""
    config = {
        WEATHER_DOMAIN: [
            {CONF_PLATFORM: DOMAIN, CONF_NAME: "Home"},
            {CONF_PLATFORM: DOMAIN, CONF_NAME: "Office"},
        ]
    }

    with patch.object(FlowManager, "async_init") as flow_init:
        assert await async_setup_component(hass, WEATHER_DOMAIN, config)
        await hass.async_block_till_done()

        assert flow_init.called
