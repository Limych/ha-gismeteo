#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging
from typing import List

import voluptuous as vol
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.weather import ATTR_FORECAST_CONDITION
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_API_KEY,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_PLATFORM,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from . import GismeteoDataUpdateCoordinator
from .const import (
    ATTR_WEATHER_CLOUDINESS,
    ATTR_WEATHER_GEOMAGNETIC_FIELD,
    ATTR_WEATHER_PRECIPITATION_AMOUNT,
    ATTR_WEATHER_PRECIPITATION_INTENSITY,
    ATTR_WEATHER_PRECIPITATION_TYPE,
    ATTR_WEATHER_STORM,
    ATTRIBUTION,
    CONF_CACHE_DIR,
    CONF_FORECAST,
    CONF_YAML,
    COORDINATOR,
    DEFAULT_NAME,
    DOMAIN,
    FORECAST_SENSOR_TYPE,
    PRECIPITATION_AMOUNT,
    SENSOR_TYPES,
)
from .entity import GismeteoEntity

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
        vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
        vol.Optional(CONF_FORECAST, default=False): cv.boolean,
        vol.Optional(CONF_CACHE_DIR): cv.string,
    }
)


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistant, config, add_entities, discovery_info=None
):
    """Set up the Gismeteo sensor platform."""
    if CONF_YAML not in hass.data[DOMAIN]:
        hass.data[DOMAIN].setdefault(CONF_YAML, {})
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data={}
            )
        )

    uid = "-".join([SENSOR_DOMAIN, config[CONF_NAME]])
    config[CONF_PLATFORM] = SENSOR_DOMAIN
    hass.data[DOMAIN][CONF_YAML][uid] = config


def fix_kinds(kinds: List[str], warn=True) -> List[str]:
    """Remove deprecated values from kinds."""
    if "weather" in kinds:
        if warn:
            _LOGGER.warning(
                'Deprecated condition "weather". Please replace it to "condition"'
            )
        kinds = set(kinds)
        kinds.remove("weather")
        kinds = list(kinds | {"condition"})

    return kinds


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add Gismeteo sensor entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, cfg in hass.data[DOMAIN][CONF_YAML].items():
            if cfg[CONF_PLATFORM] != SENSOR_DOMAIN:
                continue  # pragma: no cover

            name = cfg[CONF_NAME]
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            for kind in fix_kinds(cfg[CONF_MONITORED_CONDITIONS]):
                entities.append(GismeteoSensor(name, kind, coordinator))

            if cfg.get(CONF_FORECAST, True):
                SENSOR_TYPES["forecast"] = FORECAST_SENSOR_TYPE
                entities.append(GismeteoSensor(name, "forecast", coordinator))

    else:
        # Setup from config entry
        name = config_entry.data[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        for kind in fix_kinds(
            config_entry.data.get(CONF_MONITORED_CONDITIONS, SENSOR_TYPES.keys()),
            warn=False,
        ):
            entities.append(GismeteoSensor(name, kind, coordinator))

        if config_entry.data.get(CONF_FORECAST, True):
            SENSOR_TYPES["forecast"] = FORECAST_SENSOR_TYPE
            entities.append(GismeteoSensor(name, "forecast", coordinator))

    async_add_entities(entities, False)


class GismeteoSensor(GismeteoEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(
        self,
        name: str,
        kind: str,
        coordinator: GismeteoDataUpdateCoordinator,
    ):
        """Initialize the sensor."""
        super().__init__(name, coordinator)
        self.kind = kind
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[self.kind][ATTR_UNIT_OF_MEASUREMENT]

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._gismeteo.unique_id}-{self.kind}".lower()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_NAME]}"

    @property
    def state(self):
        """Return the state."""
        data = self._gismeteo.current
        try:
            if self.kind == "condition":
                self._state = self._gismeteo.condition()
            elif self.kind == "forecast":
                self._state = self._gismeteo.forecast()[0][ATTR_FORECAST_CONDITION]
            elif self.kind == "temperature":
                self._state = self._gismeteo.temperature()
            elif self.kind == "wind_speed":
                self._state = self._gismeteo.wind_speed_ms()
            elif self.kind == "wind_bearing":
                self._state = self._gismeteo.wind_bearing()
            elif self.kind == "humidity":
                self._state = self._gismeteo.humidity()
            elif self.kind == "pressure":
                self._state = self._gismeteo.pressure_hpa()
            elif self.kind == "clouds":
                self._state = int(data.get(ATTR_WEATHER_CLOUDINESS) * 33.33)
            elif self.kind == "rain":
                if data.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [1, 3]:
                    self._state = (
                        data.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                        or PRECIPITATION_AMOUNT[
                            data.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
                        ]
                    )
                    self._unit_of_measurement = SENSOR_TYPES[self.kind][
                        ATTR_UNIT_OF_MEASUREMENT
                    ]
                else:
                    self._state = "not raining"
                    self._unit_of_measurement = ""
            elif self.kind == "snow":
                if data.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [2, 3]:
                    self._state = (
                        data.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                        or PRECIPITATION_AMOUNT[
                            data.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
                        ]
                    )
                    self._unit_of_measurement = SENSOR_TYPES[self.kind][
                        ATTR_UNIT_OF_MEASUREMENT
                    ]
                else:
                    self._state = "not snowing"
                    self._unit_of_measurement = ""
            elif self.kind == "storm":
                self._state = data.get(ATTR_WEATHER_STORM)
            elif self.kind == "geomagnetic":
                self._state = data.get(ATTR_WEATHER_GEOMAGNETIC_FIELD)
            elif self.kind == "water_temperature":
                self._state = self._gismeteo.water_temperature()
        except KeyError:  # pragma: no cover
            self._state = None
            _LOGGER.warning("Condition is currently not available: %s", self.kind)

        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return SENSOR_TYPES[self.kind][ATTR_ICON]

    @property
    def device_class(self):
        """Return the device_class."""
        return SENSOR_TYPES[self.kind][ATTR_DEVICE_CLASS]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = self._gismeteo.attributes.copy()
        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attrs
