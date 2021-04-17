# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import (
    ENTRY_STATE_LOADED,
    ENTRY_STATE_NOT_LOADED,
    ENTRY_STATE_SETUP_RETRY,
)
from homeassistant.const import CONF_MODE, CONF_NAME, CONF_SENSORS
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.gismeteo import _convert_yaml_config
from custom_components.gismeteo.api import ApiError, GismeteoApiClient
from custom_components.gismeteo.const import (
    CONF_PLATFORM_FORMAT,
    CONF_WEATHER,
    DOMAIN,
    DOMAIN_YAML,
    FORECAST_MODE_HOURLY,
    SENSOR,
    WEATHER,
)

from .const import MOCK_CONFIG, MOCK_CONFIG_OPTIONS, MOCK_CONFIG_YAML


@pytest.fixture()
def gismeteo_config_entry():
    """Make mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test",
        unique_id="0123456",
        data=MOCK_CONFIG,
        options=MOCK_CONFIG_OPTIONS,
    )


async def test__convert_yaml_config():
    """Test _convert_yaml_config function."""
    yaml = {
        CONF_NAME: "Home",
    }
    entry = {
        CONF_NAME: "Home",
    }
    #
    assert _convert_yaml_config(yaml) == entry
    assert _convert_yaml_config(yaml) is not entry

    yaml = {
        CONF_NAME: "Home",
        CONF_WEATHER: {"qwe": "asd"},
    }
    entry = {
        CONF_NAME: "Home",
        CONF_PLATFORM_FORMAT.format(WEATHER): True,
        "qwe": "asd",
    }
    #
    assert _convert_yaml_config(yaml) == entry
    assert _convert_yaml_config(yaml) is not entry

    yaml = {
        CONF_NAME: "Home",
        CONF_SENSORS: {"asd": "zxc"},
    }
    entry = {
        CONF_NAME: "Home",
        CONF_PLATFORM_FORMAT.format(SENSOR): True,
        "asd": "zxc",
    }
    #
    assert _convert_yaml_config(yaml) == entry
    assert _convert_yaml_config(yaml) is not entry

    yaml = {
        CONF_NAME: "Home",
        CONF_WEATHER: {"qwe": "asd"},
        CONF_SENSORS: {"asd": "zxc"},
    }
    entry = {
        CONF_NAME: "Home",
        CONF_PLATFORM_FORMAT.format(WEATHER): True,
        CONF_PLATFORM_FORMAT.format(SENSOR): True,
        "qwe": "asd",
        "asd": "zxc",
    }
    #
    assert _convert_yaml_config(yaml) == entry
    assert _convert_yaml_config(yaml) is not entry


async def async_gismeteo_setup(hass: HomeAssistant, config_entry: MockConfigEntry):
    """Set up the Gismeteo integration in Home Assistant."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    return config_entry


async def test_async_setup(hass: HomeAssistant, gismeteo_api):
    """Test a successful setup component."""
    assert DOMAIN not in hass.data
    assert DOMAIN_YAML not in hass.data

    await async_setup_component(hass, DOMAIN, {DOMAIN: MOCK_CONFIG_YAML})
    await hass.async_block_till_done()

    expected_config = MOCK_CONFIG_YAML.copy()
    expected_config["home"][CONF_WEATHER] = {CONF_MODE: FORECAST_MODE_HOURLY}

    assert DOMAIN in hass.data
    assert len(hass.data[DOMAIN]) == 2
    assert "home" in hass.data[DOMAIN]
    assert DOMAIN_YAML in hass.data
    assert hass.data[DOMAIN_YAML] == expected_config

    state = hass.states.get(f"{WEATHER}.home")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR}.home_condition")
    assert state is not None
    assert state.state == "snowy"


async def test_async_setup_entry(
    hass: HomeAssistant, gismeteo_config_entry, gismeteo_api
):
    """Test a successful setup entry."""
    await async_gismeteo_setup(hass, gismeteo_config_entry)

    state = hass.states.get(f"{WEATHER}.home")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR}.home_condition")
    assert state is not None
    assert state.state == "snowy"


async def test_config_not_ready(hass: HomeAssistant, gismeteo_config_entry):
    """Test for setup failure if connection to Gismeteo is missing."""
    location_data = load_fixture("location.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        if args[0].find("/cities/") >= 0:
            return location_data
        raise ApiError

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        gismeteo_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(gismeteo_config_entry.entry_id)

        assert gismeteo_config_entry.state == ENTRY_STATE_SETUP_RETRY


async def test_unload_entry(hass: HomeAssistant, gismeteo_config_entry, gismeteo_api):
    """Test successful unload of entry."""
    entry = await async_gismeteo_setup(hass, gismeteo_config_entry)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ENTRY_STATE_LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ENTRY_STATE_NOT_LOADED
    assert not hass.data.get(DOMAIN)
