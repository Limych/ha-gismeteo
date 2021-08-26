#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_NAME, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from . import GismeteoDataUpdateCoordinator, _convert_yaml_config, deslugify
from .const import (
    ATTRIBUTION,
    CONF_PLATFORM_FORMAT,
    COORDINATOR,
    DOMAIN,
    DOMAIN_YAML,
    WEATHER,
)
from .entity import GismeteoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add a Gismeteo weather entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, cfg in hass.data[DOMAIN_YAML].items():
            cfg = _convert_yaml_config(cfg)

            if cfg.get(CONF_PLATFORM_FORMAT.format(WEATHER), False) is False:
                continue  # pragma: no cover

            location_name = cfg.get(CONF_NAME, deslugify(uid))
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            entities.append(GismeteoWeather(location_name, coordinator))

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: ConfigType
        config.update(config_entry.options)

        if config.get(CONF_PLATFORM_FORMAT.format(WEATHER), False) is False:
            return  # pragma: no cover

        location_name = config[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        entities.append(GismeteoWeather(location_name, coordinator))

    async_add_entities(entities, False)


class GismeteoWeather(GismeteoEntity, WeatherEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(self, location_name: str, coordinator: GismeteoDataUpdateCoordinator):
        """Initialize."""
        super().__init__(location_name, coordinator)
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
        return self._gismeteo.pressure()

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
        """Return the current wind speed."""
        return self._gismeteo.wind_speed_kmh()

    @property
    def forecast(self):
        """Return the forecast array."""
        return self._gismeteo.forecast()
