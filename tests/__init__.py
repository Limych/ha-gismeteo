"""Tests for GisMeteo integration."""
from unittest.mock import patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER
from homeassistant.const import CONF_MONITORED_CONDITIONS, CONF_NAME, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.gismeteo import DOMAIN, GismeteoApiClient, sensor
from custom_components.gismeteo.const import CONF_FORECAST, CONF_YAML, SENSOR_TYPES

TEST_CONFIG = {
    SENSOR_DOMAIN: [
        {
            CONF_PLATFORM: DOMAIN,
        },
        {
            CONF_PLATFORM: DOMAIN,
            CONF_NAME: "Office",
            CONF_MONITORED_CONDITIONS: list(SENSOR_TYPES.keys()),
            CONF_FORECAST: True,
        },
    ],
}


def get_mock_config_entry(
    hass: HomeAssistant, source=SOURCE_USER, forecast=False
) -> MockConfigEntry:
    """Make mock configs."""
    if source == SOURCE_USER:
        options = {}
        if forecast:
            options["forecast"] = True

        entry = MockConfigEntry(
            domain=DOMAIN,
            title="Home",
            unique_id="0123456",
            data={
                "latitude": 55.55,
                "longitude": 122.12,
                "name": "Home",
            },
            options=options,
        )
    else:
        entry = MockConfigEntry(
            domain=DOMAIN, source=SOURCE_IMPORT, title="Import", unique_id="12345"
        )
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN].setdefault(CONF_YAML, {})
        for config in TEST_CONFIG[SENSOR_DOMAIN]:
            config = sensor.PLATFORM_SCHEMA(config)  # type: ignore
            uid = "-".join([SENSOR_DOMAIN, config[CONF_NAME]])
            hass.data[DOMAIN][CONF_YAML][uid] = config

    return entry


async def init_integration(
    hass: HomeAssistant, source=SOURCE_USER, forecast=False
) -> MockConfigEntry:
    """Set up the Gismeteo integration in Home Assistant."""
    entry = get_mock_config_entry(hass, source, forecast)

    location_data = load_fixture("location.xml")
    forecast_data = load_fixture("forecast.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        return location_data if args[0].find("/cities/") >= 0 else forecast_data

    with patch.object(GismeteoApiClient, "_async_get_data", side_effect=mock_data):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry
