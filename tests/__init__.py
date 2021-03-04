"""Tests for GisMeteo integration."""
from unittest.mock import patch

from homeassistant.config_entries import ENTRY_STATE_LOADED
from homeassistant.util import utcnow
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    load_fixture,
)

from custom_components.gismeteo import DOMAIN, UPDATE_INTERVAL, Gismeteo


def get_mock_config_entry(forecast=False) -> MockConfigEntry:
    """Make mock configs."""
    options = {}
    if forecast:
        options["forecast"] = True

    return MockConfigEntry(
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


async def init_integration(hass: HomeAssistant, forecast=False) -> MockConfigEntry:
    """Set up the Gismeteo integration in Home Assistant."""
    entry = get_mock_config_entry(forecast)

    location_data = load_fixture("location.xml")
    forecast_data = load_fixture("forecast.xml")

    # pylint: disable=unused-argument
    def mock_data(*args, **kwargs):
        return location_data if args[0].find("/cities/") >= 0 else forecast_data

    with patch.object(Gismeteo, "_async_get_data", side_effect=mock_data):
        entry.add_to_hass(hass: HomeAssistant)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry


async def test_update_interval(hass: HomeAssistant):
    """Test correct update interval."""
    entry = await init_integration(hass: HomeAssistant)

    assert entry.state == ENTRY_STATE_LOADED

    future = utcnow() + UPDATE_INTERVAL

    with patch.object(Gismeteo, "async_update") as mock_current:
        assert mock_current.call_count == 0

        async_fire_time_changed(hass: HomeAssistant, future)
        await hass.async_block_till_done()

        assert mock_current.call_count == 1
