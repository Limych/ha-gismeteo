#
#  Copyright (c) 2019-2020, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Gismeteo Sensor.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""
import logging

from homeassistant.components.weather import ATTR_FORECAST_CONDITION, PLATFORM_SCHEMA
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_API_KEY,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol

from . import ATTRIBUTION, DOMAIN, GismeteoDataUpdateCoordinator
from .const import (
    ATTR_LABEL,
    ATTR_WEATHER_CLOUDINESS,
    ATTR_WEATHER_GEOMAGNETIC_FIELD,
    ATTR_WEATHER_PRECIPITATION_AMOUNT,
    ATTR_WEATHER_PRECIPITATION_INTENSITY,
    ATTR_WEATHER_PRECIPITATION_TYPE,
    ATTR_WEATHER_STORM,
    CONF_CACHE_DIR,
    CONF_FORECAST,
    CONF_LANGUAGE,
    COORDINATOR,
    DEFAULT_NAME,
    NAME,
    PRECIPITATION_AMOUNT,
    SENSOR_TYPES,
)
from .gismeteo import Gismeteo

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
        vol.Optional(CONF_LANGUAGE): cv.string,
    }
)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Gismeteo sensor platform."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=dict(config)
        )
    )

    # if None in (hass.config.latitude, hass.config.longitude):
    #     _LOGGER.error("Latitude or longitude not set in Home Assistant config")
    #     return
    # latitude = round(hass.config.latitude, 6)
    # longitude = round(hass.config.longitude, 6)
    #
    # name = config.get(CONF_NAME)
    # forecast = config.get(CONF_FORECAST)
    # cache_dir = config.get(CONF_CACHE_DIR, hass.config.path(STORAGE_DIR))
    #
    # sleep(randint(0, 5))
    # websession = async_get_clientsession(hass)
    # gism = Gismeteo(
    #     websession,
    #     latitude=latitude,
    #     longitude=longitude,
    #     params={
    #         "timezone": str(hass.config.time_zone),
    #         "cache_dir": cache_dir,
    #         "cache_time": UPDATE_INTERVAL.total_seconds(),
    #     },
    # )
    #
    # dev = []
    # for variable in config[CONF_MONITORED_CONDITIONS]:
    #     dev.append(
    #         GismeteoSensor(
    #             name,
    #             gism,
    #             variable,
    #             SENSOR_TYPES[variable][1],
    #             SENSOR_TYPES[variable][2],
    #         )
    #     )
    #
    # if forecast:
    #     SENSOR_TYPES["forecast"] = FORECAST_SENSOR_TYPE
    #     dev.append(
    #         GismeteoSensor(
    #             name,
    #             gism,
    #             "forecast",
    #             SENSOR_TYPES["forecast"][1],
    #             SENSOR_TYPES["forecast"][2],
    #         )
    #     )
    #
    # add_entities(dev, True)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Gismeteo entities from a config_entry."""
    name = config_entry.data[CONF_NAME]

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    sensors = []
    for kind in config_entry.data.get(CONF_MONITORED_CONDITIONS, SENSOR_TYPES.keys()):
        sensors.append(GismeteoSensor(name, kind, coordinator))

    # if coordinator.forecast:
    #     for sensor in FORECAST_SENSOR_TYPES:
    #         for day in FORECAST_DAYS:
    #             # Some air quality/allergy sensors are only available for certain
    #             # locations.
    #             if sensor in coordinator.data[ATTR_FORECAST][0]:
    #                 sensors.append(
    #                     GismeteoSensor(name, sensor, coordinator, forecast_day=day)
    #                 )

    async_add_entities(sensors, False)


class GismeteoSensor(CoordinatorEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(
        self,
        name: str,
        kind: str,
        coordinator: GismeteoDataUpdateCoordinator,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._name = name
        self.kind = kind
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[self.kind][ATTR_UNIT_OF_MEASUREMENT]

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {SENSOR_TYPES[self.kind][ATTR_LABEL]}"

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self.coordinator.location_key}-{self.kind}".lower()

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
    def state(self):
        """Return the state."""
        data = self._gismeteo.current
        try:
            if self.kind == "weather":
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
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
