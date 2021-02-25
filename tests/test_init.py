"""Tests for GisMeteo integration."""
from asynctest import patch
from homeassistant.config_entries import (
    ENTRY_STATE_LOADED,
    ENTRY_STATE_NOT_LOADED,
    ENTRY_STATE_SETUP_RETRY,
)
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.setup import async_setup_component

from custom_components.gismeteo import DOMAIN, ApiError

from . import get_mock_config_entry, init_integration


async def test_async_setup(hass):
    """Test a successful setup component."""
    await async_setup_component(
        hass,
        DOMAIN,
        {
            "name": "Home",
        },
    )
    await hass.async_block_till_done()


async def test_async_setup_entry(hass):
    """Test a successful setup entry."""
    await init_integration(hass)

    state = hass.states.get("weather.home")
    assert state is not None
    assert state.state != STATE_UNAVAILABLE
    assert state.state == "snowy"


async def test_config_not_ready(hass):
    """Test for setup failure if connection to AccuWeather is missing."""
    entry = get_mock_config_entry()

    with patch(
        "custom_components.gismeteo.gismeteo.Gismeteo._async_get_data",
        side_effect=ApiError("API Error"),
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)

        assert entry.state == ENTRY_STATE_SETUP_RETRY


async def test_unload_entry(hass):
    """Test successful unload of entry."""
    entry = await init_integration(hass)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ENTRY_STATE_LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ENTRY_STATE_NOT_LOADED
    assert not hass.data.get(DOMAIN)
