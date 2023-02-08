#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import asyncio
import logging
from typing import Optional

from aiohttp import ClientConnectorError
from async_timeout import timeout

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_MODE, CONF_PLATFORM
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, GismeteoApiClient
from .const import (
    CONF_CACHE_DIR,
    CONF_PLATFORMS,
    CONF_YAML,
    COORDINATOR,
    DOMAIN,
    FORECAST_MODE_HOURLY,
    PLATFORMS,
    STARTUP_MESSAGE,
    UNDO_UPDATE_LISTENER,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up component."""
    # Print startup messages
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info(STARTUP_MESSAGE)

    # Clean up old imports from configuration.yaml
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.source == SOURCE_IMPORT:
            await hass.config_entries.async_remove(entry.entry_id)

    return True


def get_gismeteo(hass: HomeAssistant, config) -> GismeteoApiClient:
    """Prepare Gismeteo instance."""
    return GismeteoApiClient(
        async_get_clientsession(hass),
        latitude=config.get(CONF_LATITUDE, hass.config.latitude),
        longitude=config.get(CONF_LONGITUDE, hass.config.longitude),
        mode=config.get(CONF_MODE, FORECAST_MODE_HOURLY),
        params={
            "timezone": str(hass.config.time_zone),
            "cache_dir": config.get(CONF_CACHE_DIR, hass.config.path(STORAGE_DIR)),
            "cache_time": UPDATE_INTERVAL.total_seconds(),
        },
    )


async def _async_get_coordinator(hass: HomeAssistant, unique_id, config: dict):
    """Prepare update coordinator instance."""
    gismeteo = get_gismeteo(hass, config)
    await gismeteo.async_get_location()

    coordinator = GismeteoDataUpdateCoordinator(hass, unique_id, gismeteo)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    return coordinator


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Gismeteo as config entry."""
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        await asyncio.sleep(12)

        platforms = set()

        for uid, cfg in hass.data[DOMAIN][CONF_YAML].items():
            platforms.add(cfg[CONF_PLATFORM])
            coordinator = await _async_get_coordinator(hass, uid, cfg)
            hass.data[DOMAIN][uid] = {
                COORDINATOR: coordinator,
            }

        undo_listener = config_entry.add_update_listener(update_listener)
        hass.data[DOMAIN][config_entry.entry_id] = {
            UNDO_UPDATE_LISTENER: undo_listener,
        }
        platforms = list(platforms)

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: dict
        config.update(config_entry.options)

        platforms = [x for x in PLATFORMS if config.get(f"{CONF_PLATFORM}_{x}", True)]

        coordinator = await _async_get_coordinator(hass, config_entry.entry_id, config)
        undo_listener = config_entry.add_update_listener(update_listener)
        hass.data[DOMAIN][config_entry.entry_id] = {
            COORDINATOR: coordinator,
            UNDO_UPDATE_LISTENER: undo_listener,
        }

    for component in platforms:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry) -> bool:
    """Unload a config entry."""
    platforms = config_entry.data.get(CONF_PLATFORMS, [SENSOR_DOMAIN, WEATHER_DOMAIN])

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in platforms
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class GismeteoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Gismeteo data API."""

    def __init__(
        self, hass: HomeAssistant, unique_id: Optional[str], gismeteo: GismeteoApiClient
    ):
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

        self.gismeteo = gismeteo
        self._unique_id = unique_id

    @property
    def unique_id(self):
        """Return a unique_id."""
        return self._unique_id

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await self.gismeteo.async_update()
            return self.gismeteo.current
        except (ApiError, ClientConnectorError) as error:
            raise UpdateFailed(error) from error
