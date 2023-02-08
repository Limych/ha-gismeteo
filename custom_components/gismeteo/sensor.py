#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging
from typing import List

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.components.weather import ATTR_FORECAST_CONDITION
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
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
    CONF_CACHE_DIR,
    CONF_FORECAST,
    CONF_YAML,
    COORDINATOR,
    DEFAULT_NAME,
    DOMAIN,
    FORECAST_SENSOR_TYPE,
    PRECIPITATION_AMOUNT,
    SENSOR,
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

    uid = "-".join([SENSOR, config[CONF_NAME]])
    config[CONF_PLATFORM] = SENSOR
    hass.data[DOMAIN][CONF_YAML][uid] = config


def fix_kinds(kinds: List[str], warn=True) -> List[str]:
    """Remove unwanted values from kinds."""
    kinds = set(kinds)

    for k in ["forecast", "pressure_mmhg", "weather"]:
        if k in kinds:
            kinds.remove(k)

            if k == "weather":
                kinds = kinds | {"condition"}
                if warn:
                    _LOGGER.warning(
                        'Deprecated condition "weather". Please replace it to "condition"'
                    )

    kinds = list(kinds)
    kinds.sort()
    return kinds


def _gen_entities(
    location_name: str,
    coordinator: GismeteoDataUpdateCoordinator,
    config: dict,
    warn: bool,
):
    """Generate entities."""
    entities = []

    for k in fix_kinds(
        config.get(CONF_MONITORED_CONDITIONS, SENSOR_TYPES.keys()),
        warn=warn,
    ):
        entities.append(GismeteoSensor(location_name, k, coordinator, config))
        if k == "pressure":
            entities.append(
                GismeteoSensor(location_name, "pressure_mmhg", coordinator, config)
            )

    if config.get(CONF_FORECAST, False):
        SENSOR_TYPES["forecast"] = FORECAST_SENSOR_TYPE
        entities.append(GismeteoSensor(location_name, "forecast", coordinator, config))

    return entities


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Add Gismeteo sensor entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, cfg in hass.data[DOMAIN][CONF_YAML].items():
            if cfg[CONF_PLATFORM] != SENSOR:
                continue  # pragma: no cover

            location_name = cfg[CONF_NAME]
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            entities.extend(
                _gen_entities(
                    location_name,
                    coordinator,
                    cfg,
                    True,
                )
            )

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: dict
        config.update(config_entry.options)

        location_name = config[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        entities.extend(
            _gen_entities(
                location_name,
                coordinator,
                config,
                False,
            )
        )

    async_add_entities(entities, False)


class GismeteoSensor(GismeteoEntity, SensorEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(
        self,
        location_name: str,
        kind: str,
        coordinator: GismeteoDataUpdateCoordinator,
        config: dict,
    ):
        """Initialize the sensor."""
        super().__init__(location_name, coordinator, config)

        self._kind = kind

        self._attr_unique_id = f"{self.coordinator.unique_id}-{kind}".lower()

        self._attr_device_class = SENSOR_TYPES[kind][ATTR_DEVICE_CLASS]
        self._attr_icon = SENSOR_TYPES[kind][ATTR_ICON]
        self._attr_name = f"{self._location_name} {SENSOR_TYPES[kind][ATTR_NAME]}"
        self._attr_native_unit_of_measurement = SENSOR_TYPES[kind][
            ATTR_UNIT_OF_MEASUREMENT
        ]

        self._state = None

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        data = self._gismeteo.current
        try:
            if self._kind == "condition":
                self._state = self._gismeteo.condition()
            elif self._kind == "forecast":
                self._state = self._gismeteo.forecast()[0][ATTR_FORECAST_CONDITION]
            elif self._kind == "temperature":
                self._state = self._gismeteo.temperature()
            elif self._kind == "temperature_feels_like":
                self._state = self._gismeteo.temperature_feels_like()
            elif self._kind == "wind_speed":
                self._state = self._gismeteo.wind_speed_ms()
            elif self._kind == "wind_bearing":
                self._state = self._gismeteo.wind_bearing()
            elif self._kind == "humidity":
                self._state = self._gismeteo.humidity()
            elif self._kind == "pressure":
                self._state = self._gismeteo.pressure_hpa()
            elif self._kind == "pressure_mmhg":
                self._state = self._gismeteo.pressure_mmhg()
            elif self._kind == "clouds":
                self._state = int(data.get(ATTR_WEATHER_CLOUDINESS) * 100 / 3)
            elif self._kind == "rain":
                self._state = (
                    (
                        data.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                        or PRECIPITATION_AMOUNT[
                            data.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
                        ]
                    )
                    if data.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [1, 3]
                    else 0
                )
            elif self._kind == "snow":
                self._state = (
                    (
                        data.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
                        or PRECIPITATION_AMOUNT[
                            data.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
                        ]
                    )
                    if data.get(ATTR_WEATHER_PRECIPITATION_TYPE) in [2, 3]
                    else 0
                )
            elif self._kind == "storm":
                self._state = data.get(ATTR_WEATHER_STORM)
            elif self._kind == "geomagnetic":
                self._state = data.get(ATTR_WEATHER_GEOMAGNETIC_FIELD)
            elif self._kind == "water_temperature":
                self._state = self._gismeteo.water_temperature()

        except KeyError:  # pragma: no cover
            self._state = None
            _LOGGER.warning("Condition is currently not available: %s", self._kind)

        return self._state
