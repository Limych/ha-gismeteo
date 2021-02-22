"""Tests for GisMeteo integration."""
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture

from custom_components.gismeteo import DOMAIN


async def init_integration(hass, forecast=False) -> MockConfigEntry:
    """Set up the Gismeteo integration in Home Assistant."""
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

    forecast = load_fixture("forecast_data.xml")

    with patch(
        "custom_components.gismeteo.Gismeteo._get_nearest_city_id",
        return_value=372,
    ), patch(
        "custom_components.gismeteo.Gismeteo._http_request",
        return_value=forecast,
    ):
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    return entry
