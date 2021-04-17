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
    CONF_PLATFORM,
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
VERSION = "3.0.0.dev0"
ATTRIBUTION = "Data provided by Gismeteo"
ISSUE_URL = "https://github.com/Limych/ha-gismeteo/issues"
DOMAIN_YAML = DOMAIN + "_yaml"

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
CONF_WEATHER = "weather"
CONF_CACHE_DIR = "cache_dir"
CONF_FORECAST = "forecast"
CONF_PLATFORM_FORMAT = CONF_PLATFORM + "_{}"

FORECAST_MODE_HOURLY = "hourly"
FORECAST_MODE_DAILY = "daily"

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
ATTR_WEATHER_ALLERGY_BIRCH = "allergy_birch"
ATTR_WEATHER_UV_INDEX = "uv_index"
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
ATTR_FORECAST_ALLERGY_BIRCH = ATTR_WEATHER_ALLERGY_BIRCH
ATTR_FORECAST_UV_INDEX = ATTR_WEATHER_UV_INDEX

COORDINATOR = "coordinator"
UNDO_UPDATE_LISTENER = "undo_update_listener"


ENDPOINT_URL = "https://services.gismeteo.ru/inform-service/inf_chrome"
#
PARSER_URL_TPL = "https://www.gismeteo.ru/weather-{}-{}/10-days/"
PARSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81"

UPDATE_INTERVAL = timedelta(minutes=5)
PARSED_UPDATE_INTERVAL = timedelta(minutes=61)

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

DEVICE_CLASS_FORMAT = DOMAIN + "__{}"

SENSOR_TYPES = {
    "weather": {},  # => condition
    "condition": {
        ATTR_NAME: "Condition",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_FORMAT.format("condition"),
    },
    "temperature": {
        ATTR_NAME: "Temperature",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    "temperature_feels_like": {
        ATTR_NAME: "Temperature Feels Like",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    "humidity": {
        ATTR_NAME: "Humidity",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY,
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "pressure": {
        ATTR_NAME: "Pressure",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PRESSURE,
        ATTR_UNIT_OF_MEASUREMENT: PRESSURE_HPA,
    },
    "pressure_mmhg": {
        ATTR_NAME: "Pressure mmHg",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_PRESSURE,
        ATTR_UNIT_OF_MEASUREMENT: "mmHg",
    },
    "wind_speed": {
        ATTR_NAME: "Wind speed",
        ATTR_ICON: "mdi:weather-windy",
        ATTR_UNIT_OF_MEASUREMENT: SPEED_METERS_PER_SECOND,
    },
    "wind_bearing": {
        ATTR_NAME: "Wind bearing",
        ATTR_ICON: "mdi:weather-windy",
        ATTR_UNIT_OF_MEASUREMENT: DEGREE,
    },
    "clouds": {
        ATTR_NAME: "Cloud coverage",
        ATTR_ICON: "mdi:weather-partly-cloudy",
        ATTR_UNIT_OF_MEASUREMENT: PERCENTAGE,
    },
    "rain": {
        ATTR_NAME: "Rain",
        ATTR_ICON: "mdi:weather-rainy",
        ATTR_UNIT_OF_MEASUREMENT: LENGTH_MILLIMETERS,
    },
    "snow": {
        ATTR_NAME: "Snow",
        ATTR_ICON: "mdi:weather-snowy",
        ATTR_UNIT_OF_MEASUREMENT: LENGTH_MILLIMETERS,
    },
    "storm": {
        ATTR_NAME: "Storm",
        ATTR_ICON: "mdi:weather-lightning",
    },
    "geomagnetic": {
        ATTR_NAME: "Geomagnetic field",
        ATTR_ICON: "mdi:magnet-on",
        ATTR_UNIT_OF_MEASUREMENT: "",
    },
    "water_temperature": {
        ATTR_NAME: "Water Temperature",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
}
