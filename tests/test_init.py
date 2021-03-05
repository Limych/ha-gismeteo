"""Tests for GisMeteo integration."""
# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.config_entries import (
    ENTRY_STATE_LOADED,
    ENTRY_STATE_NOT_LOADED,
    ENTRY_STATE_SETUP_RETRY,
)
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.gismeteo.api import ApiError, GismeteoApiClient
from custom_components.gismeteo.const import CONF_FORECAST, DOMAIN


@pytest.fixture()
def gismeteo_config():
    """Make mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Home",
        unique_id="0123456",
        data={
            CONF_NAME: "Home",
            CONF_LATITUDE: 55.55,
            CONF_LONGITUDE: 122.12,
            CONF_FORECAST: True,
        },
    )


@pytest.fixture()
async def gismeteo_entry(
    hass: HomeAssistant, gismeteo_config: MockConfigEntry, gismeteo_api
) -> MockConfigEntry:
    """Set up the Gismeteo integration in Home Assistant."""
    gismeteo_config.add_to_hass(hass)
    await hass.config_entries.async_setup(gismeteo_config.entry_id)
    await hass.async_block_till_done()

    return gismeteo_config


async def test_async_setup(hass: HomeAssistant):
    """Test a successful setup component."""
    await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_async_setup_entry(hass: HomeAssistant, gismeteo_entry):
    """Test a successful setup entry."""
    state = hass.states.get(f"{WEATHER_DOMAIN}.home")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR_DOMAIN}.home_condition")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR_DOMAIN}.home_forecast")
    assert state is not None
    assert state.state == "clear-night"


async def test_config_not_ready(hass: HomeAssistant, gismeteo_config):
    """Test for setup failure if connection to Gismeteo is missing."""
    location_data = load_fixture("location.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        if args[0].find("/cities/") >= 0:
            return location_data
        raise ApiError

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        gismeteo_config.add_to_hass(hass)
        await hass.config_entries.async_setup(gismeteo_config.entry_id)

        assert gismeteo_config.state == ENTRY_STATE_SETUP_RETRY


async def test_unload_entry(hass: HomeAssistant, gismeteo_entry: MockConfigEntry):
    """Test successful unload of entry."""
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert gismeteo_entry.state == ENTRY_STATE_LOADED

    assert await hass.config_entries.async_unload(gismeteo_entry.entry_id)
    await hass.async_block_till_done()

    assert gismeteo_entry.state == ENTRY_STATE_NOT_LOADED
    assert not hass.data.get(DOMAIN)
