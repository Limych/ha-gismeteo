#
#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import asyncio
import logging

from aiohttp import ClientConnectorError
from async_timeout import timeout
from homeassistant.const import CONF_MODE
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    COORDINATOR,
    FORECAST_MODE_HOURLY,
    UNDO_UPDATE_LISTENER,
    UPDATE_INTERVAL,
)
from .gismeteo import ApiError, Gismeteo

_LOGGER = logging.getLogger(__name__)

# Base component constants
DOMAIN = "gismeteo"
VERSION = "dev"
ISSUE_URL = "https://github.com/Limych/ha-gismeteo/issues"
ATTRIBUTION = "Data provided by Gismeteo"

PLATFORMS = ["sensor", "weather"]


# pylint: disable=unused-argument
async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up component."""
    # Print startup message
    _LOGGER.info("Version %s", VERSION)
    _LOGGER.info(
        "If you have ANY issues with this, please report them here: %s", ISSUE_URL
    )

    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    """Set up AccuWeather as config entry."""
    location_key = config_entry.unique_id
    forecast = config_entry.options.get(CONF_MODE, FORECAST_MODE_HOURLY)

    _LOGGER.debug("Using location_key: %s", location_key)

    websession = async_get_clientsession(hass)

    coordinator = GismeteoDataUpdateCoordinator(
        hass, websession, location_key, forecast
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class GismeteoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gismeteo data API."""

    def __init__(self, hass, session, location_key, mode):
        """Initialize."""
        self.location_key = location_key
        self.is_metric = hass.config.units.is_metric
        self.gismeteo = Gismeteo(session, location_key=self.location_key, mode=mode)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await self.gismeteo.async_update()
                current = self.gismeteo.current
        except (ApiError, ClientConnectorError) as error:
            raise UpdateFailed(error) from error

        return current
