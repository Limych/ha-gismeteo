#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from datetime import timedelta

from homeassistant.components.sensor import DOMAIN as SENSOR
from homeassistant.components.weather import ATTR_FORECAST_CONDITION
from homeassistant.components.weather import DOMAIN as WEATHER
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    DEGREE,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_MILLIMETERS,
    PERCENTAGE,
    PRESSURE_HPA,
    SPEED_METERS_PER_SECOND,
    TEMP_CELSIUS,
)

# Base component constants
NAME = "Gismeteo"
DOMAIN = "gismeteo"
VERSION = "2.3.1"
ATTRIBUTION = "Data provided by Gismeteo"
ISSUE_URL = "https://github.com/Limych/ha-gismeteo/issues"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Platforms
PLATFORMS = [SENSOR, WEATHER]

# Configuration and options
CONF_CACHE_DIR = "cache_dir"
CONF_FORECAST = "forecast"
CONF_PLATFORMS = "platforms"
CONF_YAML = "_yaml"

FORECAST_MODE_HOURLY = "hourly"
FORECAST_MODE_DAILY = "daily"

# Defaults
DEFAULT_NAME = "Gismeteo"

# Attributes
ATTR_SUNRISE = "sunrise"
ATTR_SUNSET = "sunset"
#
ATTR_WEATHER_CONDITION = ATTR_FORECAST_CONDITION
ATTR_WEATHER_CLOUDINESS = "cloudiness"
ATTR_WEATHER_PRECIPITATION_TYPE = "precipitation_type"
ATTR_WEATHER_PRECIPITATION_AMOUNT = "precipitation_amount"
ATTR_WEATHER_PRECIPITATION_INTENSITY = "precipitation_intensity"
ATTR_WEATHER_STORM = "storm"
ATTR_WEATHER_GEOMAGNETIC_FIELD = "gm_field"
ATTR_WEATHER_PHENOMENON = "phenomenon"
ATTR_WEATHER_WATER_TEMPERATURE = "water_temperature"
#
ATTR_FORECAST_HUMIDITY = "humidity"
ATTR_FORECAST_PRESSURE = "pressure"
ATTR_FORECAST_CLOUDINESS = ATTR_WEATHER_CLOUDINESS
ATTR_FORECAST_PRECIPITATION_TYPE = ATTR_WEATHER_PRECIPITATION_TYPE
ATTR_FORECAST_PRECIPITATION_AMOUNT = ATTR_WEATHER_PRECIPITATION_AMOUNT
ATTR_FORECAST_PRECIPITATION_INTENSITY = ATTR_WEATHER_PRECIPITATION_INTENSITY
ATTR_FORECAST_STORM = ATTR_WEATHER_STORM
ATTR_FORECAST_GEOMAGNETIC_FIELD = ATTR_WEATHER_GEOMAGNETIC_FIELD
ATTR_FORECAST_PHENOMENON = ATTR_WEATHER_PHENOMENON


ENDPOINT_URL = "https://services.gismeteo.ru/inform-service/inf_chrome"

UPDATE_INTERVAL = timedelta(minutes=5)

CONDITION_FOG_CLASSES = [
    11,
    12,
    28,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    120,
    130,
    131,
    132,
    133,
    134,
    135,
    528,
]

MMHG2HPA = 1.333223684
MS2KMH = 3.6

PRECIPITATION_AMOUNT = (0, 2, 6, 16)

DEVICE_CLASS_TPL = DOMAIN + "__{}"

SENSOR_TYPES = {
    "weather": {},  # => condition
    "condition": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TPL.format("condition"),
        ATTR_ICON: None,
        ATTR_NAME: "Condition",
        ATTR_UNIT_OF_MEASUREMENT: None,
    },
    "temperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Temperature",
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    "temperature_feels_like": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Temperature Feels Like",
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    "humidity": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY,
        ATTR_ICON: None,
        ATTR_NAME: "Humidity",
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "pressure": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PRESSURE,
        ATTR_ICON: None,
        ATTR_NAME: "Pressure",
        ATTR_UNIT_OF_MEASUREMENT: PRESSURE_HPA,
    },
    "pressure_mmhg": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PRESSURE,
        ATTR_ICON: None,
        ATTR_NAME: "Pressure mmHg",
        ATTR_UNIT_OF_MEASUREMENT: "mmHg",
    },
    "wind_speed": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_NAME: "Wind speed",
        ATTR_UNIT_OF_MEASUREMENT: SPEED_METERS_PER_SECOND,
    },
    "wind_bearing": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-windy",
        ATTR_NAME: "Wind bearing",
        ATTR_UNIT_OF_MEASUREMENT: DEGREE,
    },
    "clouds": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-partly-cloudy",
        ATTR_NAME: "Cloud coverage",
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "rain": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_NAME: "Rain",
        ATTR_UNIT_OF_MEASUREMENT: LENGTH_MILLIMETERS,
    },
    "snow": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-snowy",
        ATTR_NAME: "Snow",
        ATTR_UNIT_OF_MEASUREMENT: LENGTH_MILLIMETERS,
    },
    "storm": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:weather-lightning",
        ATTR_NAME: "Storm",
        ATTR_UNIT_OF_MEASUREMENT: None,
    },
    "geomagnetic": {
        ATTR_DEVICE_CLASS: None,
        ATTR_ICON: "mdi:magnet-on",
        ATTR_NAME: "Geomagnetic field",
        ATTR_UNIT_OF_MEASUREMENT: "",
    },
    "water_temperature": {
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_ICON: None,
        ATTR_NAME: "Water Temperature",
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
}
FORECAST_SENSOR_TYPE = {
    ATTR_DEVICE_CLASS: DEVICE_CLASS_TPL.format("condition"),
    ATTR_ICON: None,
    ATTR_NAME: "3h Forecast",
    ATTR_UNIT_OF_MEASUREMENT: None,
}

COORDINATOR = "coordinator"
UNDO_UPDATE_LISTENER = "undo_update_listener"
