"""Tests for GisMeteo integration."""
# pylint: disable=redefined-outer-name
from typing import Optional
from unittest.mock import patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_SENSORS
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.gismeteo import _convert_yaml_config, deslugify
from custom_components.gismeteo.api import ApiError, GismeteoApiClient
from custom_components.gismeteo.const import (
    CONF_PLATFORM_FORMAT,
    CONF_WEATHER,
    DOMAIN,
    DOMAIN_YAML,
)

from .const import (
    FAKE_CONFIG,
    FAKE_CONFIG_OPTIONS,
    FAKE_CONFIG_YAML,
    FAKE_NAME,
    FAKE_UNIQUE_ID,
)


async def test_deslugify():
    """Test deslugify string."""
    assert deslugify("") == ""
    assert deslugify("qwe") == "Qwe"
    assert deslugify("asd_zxc__qwe") == "Asd zxc  qwe"


async def async_init_integration(
    hass: HomeAssistant,
    config_entry: Optional[ConfigEntry] = None,
) -> MockConfigEntry:
    """Set up the Gismeteo integration in Home Assistant."""
    if config_entry is None:
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            title=FAKE_NAME,
            unique_id=FAKE_UNIQUE_ID,
            data=FAKE_CONFIG,
            options=FAKE_CONFIG_OPTIONS,
        )

    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    return config_entry


async def test_async_setup(hass: HomeAssistant):
    """Test a successful setup component."""
    await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_async_setup_yaml(hass: HomeAssistant):
    """Test a successful setup component from YAML."""
    with patch.object(hass.config_entries.flow, "async_init") as init:
        await async_setup_component(hass, DOMAIN, {DOMAIN: FAKE_CONFIG_YAML})
        await hass.async_block_till_done()

        assert hass.data[DOMAIN_YAML] == FAKE_CONFIG_YAML
        assert init.call_count == 1


def test__convert_yaml_config():
    """Test convert YAML config to EntryFlow config."""
    assert _convert_yaml_config({}) == {}
    assert _convert_yaml_config({"qwe": "asd"}) == {"qwe": "asd"}

    cfg = {
        CONF_WEATHER: {"asd": "zxc"},
    }
    expected = {
        "asd": "zxc",
        CONF_PLATFORM_FORMAT.format(WEATHER_DOMAIN): True,
    }
    assert _convert_yaml_config(cfg) == expected

    cfg = {
        CONF_SENSORS: {"zxc": "qwe"},
    }
    expected = {
        "zxc": "qwe",
        CONF_PLATFORM_FORMAT.format(SENSOR_DOMAIN): True,
    }
    assert _convert_yaml_config(cfg) == expected


async def test_async_setup_entry(hass: HomeAssistant, gismeteo_api):
    """Test a successful setup entry."""
    await async_init_integration(hass)

    state = hass.states.get(f"{WEATHER_DOMAIN}.home")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR_DOMAIN}.home_condition")
    assert state is not None
    assert state.state == "snowy"


async def test_async_setup_entry_yaml(hass: HomeAssistant, gismeteo_api):
    """Test a successful setup entry from YAML."""
    hass.data[DOMAIN_YAML] = FAKE_CONFIG_YAML

    await async_init_integration(
        hass,
        MockConfigEntry(
            domain=DOMAIN,
            source=SOURCE_IMPORT,
            title=FAKE_NAME,
            unique_id=FAKE_UNIQUE_ID,
            data={},
        ),
    )

    state = hass.states.get(f"{WEATHER_DOMAIN}.home")
    assert state is not None
    assert state.state == "snowy"

    state = hass.states.get(f"{SENSOR_DOMAIN}.home_condition")
    assert state is not None
    assert state.state == "snowy"


async def test_config_not_ready(hass: HomeAssistant):
    """Test for setup failure if connection to Gismeteo is missing."""
    location_data = load_fixture("location.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        if args[0].find("/cities/") >= 0:
            return location_data
        raise ApiError

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        entry = await async_init_integration(hass)

        assert entry.state == ConfigEntryState.SETUP_RETRY


async def test_unload_entry(hass: HomeAssistant, gismeteo_api):
    """Test successful unload of entry."""
    entry = await async_init_integration(hass)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
    assert not hass.data.get(DOMAIN)
