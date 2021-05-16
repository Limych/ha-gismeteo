#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import asyncio
import logging
from typing import List, Optional

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from aiohttp import ClientConnectorError
from async_timeout import timeout
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SENSORS,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, GismeteoApiClient
from .const import (
    CONF_CACHE_DIR,
    CONF_FORECAST,
    CONF_FORECAST_DAYS,
    CONF_PLATFORM_FORMAT,
    CONF_WEATHER,
    COORDINATOR,
    DOMAIN,
    DOMAIN_YAML,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    PLATFORMS,
    SENSOR,
    SENSOR_TYPES,
    STARTUP_MESSAGE,
    UNDO_UPDATE_LISTENER,
    UPDATE_INTERVAL,
    WEATHER,
)

_LOGGER = logging.getLogger(__name__)


WEATHER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_MODE, default=FORECAST_MODE_HOURLY): vol.In(
            [FORECAST_MODE_HOURLY, FORECAST_MODE_DAILY]
        ),
    }
)

SENSORS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FORECAST_DAYS): cv.positive_int,
        vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
        vol.Optional(CONF_FORECAST): cv.deprecated,
    }
)

LOCATION_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_WEATHER): WEATHER_SCHEMA,
        vol.Optional(CONF_SENSORS): SENSORS_SCHEMA,
        vol.Optional(CONF_CACHE_DIR): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: cv.schema_with_slug_keys(LOCATION_SCHEMA)}, extra=vol.ALLOW_EXTRA
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up component."""
    if DOMAIN not in hass.data:
        _LOGGER.info(STARTUP_MESSAGE)
        hass.data[DOMAIN] = {}

    if DOMAIN not in config:
        return True

    hass.data[DOMAIN_YAML] = config[DOMAIN]
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data={}
        )
    )

    return True


def _get_api_client(hass: HomeAssistant, config: ConfigType) -> GismeteoApiClient:
    """Prepare Gismeteo API client instance."""
    return GismeteoApiClient(
        async_get_clientsession(hass),
        latitude=config.get(CONF_LATITUDE, hass.config.latitude),
        longitude=config.get(CONF_LONGITUDE, hass.config.longitude),
        mode=config.get(CONF_MODE, FORECAST_MODE_HOURLY),
        params={
            "domain": DOMAIN,
            "timezone": str(hass.config.time_zone),
            "cache_dir": config.get(CONF_CACHE_DIR, hass.config.path(STORAGE_DIR)),
            "cache_time": UPDATE_INTERVAL.total_seconds(),
        },
    )


async def _async_get_coordinator(hass: HomeAssistant, unique_id, config: dict):
    """Prepare update coordinator instance."""
    gismeteo = _get_api_client(hass, config)
    await gismeteo.async_update_location()

    coordinator = GismeteoDataUpdateCoordinator(hass, unique_id, gismeteo)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    return coordinator


def _convert_yaml_config(config: ConfigType) -> ConfigType:
    """Convert YAML config to EntryFlow config."""
    cfg = config.copy()

    if CONF_WEATHER in cfg:
        cfg.update(cfg[CONF_WEATHER])
        cfg.pop(CONF_WEATHER)
        cfg[CONF_PLATFORM_FORMAT.format(WEATHER)] = True

    if CONF_SENSORS in cfg:
        cfg.update(cfg[CONF_SENSORS])
        cfg.pop(CONF_SENSORS)
        cfg[CONF_PLATFORM_FORMAT.format(SENSOR)] = True

    return cfg


def _get_platforms(config: ConfigType) -> List[str]:
    """Get configured platforms."""
    return [x for x in PLATFORMS if config.get(CONF_PLATFORM_FORMAT.format(x), True)]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Gismeteo as config entry."""
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        platforms = set()

        for uid, cfg in hass.data[DOMAIN_YAML].items():
            cfg = _convert_yaml_config(cfg)

            platforms.update(_get_platforms(cfg))

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
        config = config_entry.data.copy()  # type: ConfigType
        config.update(config_entry.options)

        platforms = _get_platforms(config)

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


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
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


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
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
            return self.gismeteo.current_data

        except (ApiError, ClientConnectorError) as error:
            raise UpdateFailed(error) from error
