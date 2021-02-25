#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Gismeteo Weather Provider.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""
import logging

from homeassistant.components.weather import PLATFORM_SCHEMA, WeatherEntity
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_NAME,
    TEMP_CELSIUS,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol

from . import ATTRIBUTION, DOMAIN, GismeteoDataUpdateCoordinator
from .const import (
    CONF_CACHE_DIR,
    COORDINATOR,
    DEFAULT_NAME,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    NAME,
)
from .gismeteo import Gismeteo

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
        vol.Optional(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_MODE, default=FORECAST_MODE_HOURLY): vol.In(
            [FORECAST_MODE_HOURLY, FORECAST_MODE_DAILY]
        ),
        vol.Optional(CONF_CACHE_DIR): cv.string,
    }
)


# pylint: disable=unused-argument
async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Gismeteo weather platform."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config)
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a Gismeteo weather entity from a config_entry."""
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    async_add_entities([GismeteoWeather(name, coordinator)], False)


class GismeteoWeather(CoordinatorEntity, WeatherEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, name: str, coordinator: GismeteoDataUpdateCoordinator):
        """Initialize."""
        super().__init__(coordinator)

        self._name = name
        self._attrs = {}

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return self.coordinator.location_key

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.location_key)},
            "name": NAME,
            "entry_type": "service",
        }

    @property
    def _gismeteo(self) -> Gismeteo:
        return self.coordinator.gismeteo

    @property
    def condition(self):
        """Return the current condition."""
        return self._gismeteo.condition()

    @property
    def temperature(self):
        """Return the current temperature."""
        return self._gismeteo.temperature()

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the current pressure."""
        return self._gismeteo.pressure_hpa()

    @property
    def humidity(self):
        """Return the name of the sensor."""
        return self._gismeteo.humidity()

    @property
    def wind_bearing(self):
        """Return the current wind bearing."""
        return self._gismeteo.wind_bearing()

    @property
    def wind_speed(self):
        """Return the current windspeed."""
        return self._gismeteo.wind_speed_kmh()

    @property
    def forecast(self):
        """Return the forecast array."""
        return self._gismeteo.forecast()
