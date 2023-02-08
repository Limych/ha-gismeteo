#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging

import voluptuous as vol

from homeassistant.components.weather import PLATFORM_SCHEMA, WeatherEntity
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MODE,
    CONF_NAME,
    CONF_PLATFORM,
    PRESSURE_MMHG,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from . import GismeteoDataUpdateCoordinator
from .const import (
    ATTRIBUTION,
    CONF_CACHE_DIR,
    CONF_YAML,
    COORDINATOR,
    DEFAULT_NAME,
    DOMAIN,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    WEATHER,
)
from .entity import GismeteoEntity

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
async def async_setup_platform(
    hass: HomeAssistant, config, add_entities, discovery_info=None
):
    """Set up the Gismeteo weather platform."""
    if CONF_YAML not in hass.data[DOMAIN]:
        hass.data[DOMAIN].setdefault(CONF_YAML, {})
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data={}
            )
        )

    uid = WEATHER + config[CONF_NAME]
    config[CONF_PLATFORM] = WEATHER
    hass.data[DOMAIN][CONF_YAML][uid] = config


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add a Gismeteo weather entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, config in hass.data[DOMAIN][CONF_YAML].items():
            if config[CONF_PLATFORM] != WEATHER:
                continue  # pragma: no cover

            name = config[CONF_NAME]
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            entities.append(GismeteoWeather(name, coordinator, config))

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: dict
        config.update(config_entry.options)

        name = config[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        entities.append(GismeteoWeather(name, coordinator, config))

    async_add_entities(entities, False)


class GismeteoWeather(GismeteoEntity, WeatherEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(
        self,
        location_name: str,
        coordinator: GismeteoDataUpdateCoordinator,
        config: dict,
    ):
        """Initialize."""
        super().__init__(location_name, coordinator, config)
        self._attrs = {}

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return self.coordinator.unique_id

    @property
    def name(self):
        """Return the name."""
        return self._location_name

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def condition(self):
        """Return the current condition."""
        return self._gismeteo.condition()

    @property
    def native_temperature(self):
        """Return the current temperature."""
        return self._gismeteo.temperature()

    @property
    def native_temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def native_pressure(self):
        """Return the current pressure."""
        return self._gismeteo.pressure_mmhg()

    @property
    def native_pressure_unit(self):
        """Return the unit of measurement."""
        return PRESSURE_MMHG

    @property
    def humidity(self):
        """Return the name of the sensor."""
        return self._gismeteo.humidity()

    @property
    def wind_bearing(self):
        """Return the current wind bearing."""
        return self._gismeteo.wind_bearing()

    @property
    def native_wind_speed(self):
        """Return the current windspeed."""
        return self._gismeteo.wind_speed_kmh()

    @property
    def native_wind_speed_unit(self):
        """Return the native unit of measurement for wind speed."""
        return SPEED_KILOMETERS_PER_HOUR

    @property
    def forecast(self):
        """Return the forecast array."""
        return self._gismeteo.forecast()
