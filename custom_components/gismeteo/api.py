#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from collections.abc import Callable
from datetime import datetime
from http import HTTPStatus
import logging
import math
import time
from typing import Any, Dict, Optional
import xml.etree.ElementTree as etree  # type: ignore

from aiohttp import ClientSession

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
    ATTR_CONDITION_WINDY_VARIANT,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
)
from homeassistant.const import ATTR_ID, ATTR_NAME, STATE_UNKNOWN
from homeassistant.util import dt as dt_util

from .cache import Cache
from .const import (
    ATTR_FORECAST_CLOUDINESS,
    ATTR_FORECAST_GEOMAGNETIC_FIELD,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_PRECIPITATION_AMOUNT,
    ATTR_FORECAST_PRECIPITATION_INTENSITY,
    ATTR_FORECAST_PRECIPITATION_TYPE,
    ATTR_FORECAST_PRESSURE,
    ATTR_FORECAST_STORM,
    ATTR_LAST_UPDATED,
    ATTR_SUNRISE,
    ATTR_SUNSET,
    ATTR_WEATHER_CLOUDINESS,
    ATTR_WEATHER_CONDITION,
    ATTR_WEATHER_GEOMAGNETIC_FIELD,
    ATTR_WEATHER_PHENOMENON,
    ATTR_WEATHER_PRECIPITATION_AMOUNT,
    ATTR_WEATHER_PRECIPITATION_INTENSITY,
    ATTR_WEATHER_PRECIPITATION_TYPE,
    ATTR_WEATHER_STORM,
    ATTR_WEATHER_WATER_TEMPERATURE,
    CONDITION_FOG_CLASSES,
    ENDPOINT_URL,
    FORECAST_MAX_CACHE_INTERVAL,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    LOCATION_MAX_CACHE_INTERVAL,
    MMHG2HPA,
    MS2KMH,
)

_LOGGER = logging.getLogger(__name__)


class InvalidCoordinatesError(Exception):
    """Raised when coordinates are invalid."""

    def __init__(self, status):
        """Initialize."""
        super().__init__(status)
        self.status = status


class ApiError(Exception):
    """Raised when Gismeteo API request ended in error."""

    def __init__(self, status):
        """Initialize."""
        super().__init__(status)
        self.status = status


class GismeteoApiClient:
    """Gismeteo API implementation."""

    def __init__(
        self,
        session: ClientSession,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        location_key: Optional[int] = None,
        mode=FORECAST_MODE_HOURLY,
        params: Optional[dict] = None,
    ):
        """Initialize."""
        params = params or {}

        if not location_key:
            if not self._valid_coordinates(latitude, longitude):
                raise InvalidCoordinatesError("Your coordinates are invalid.")

        _LOGGER.debug("Place coordinates: %s, %s", latitude, longitude)
        _LOGGER.debug("Forecast mode: %s", mode)

        self._session = session
        self._mode = mode
        self._cache = Cache(params) if params.get("cache_dir") is not None else None
        self._latitude = latitude
        self._longitude = longitude
        self._attributes: Dict[str, Any] = {
            ATTR_ID: location_key,
        }

        self._last_updated = None
        self._current = {}
        self._forecast = []
        self._timezone = (
            dt_util.get_time_zone(params.get("timezone"))
            if params.get("timezone") is not None
            else dt_util.DEFAULT_TIME_ZONE
        )

    @staticmethod
    def _valid_coordinates(latitude: float, longitude: float) -> bool:
        """Return True if coordinates are valid."""
        try:
            assert isinstance(latitude, (int, float)) and isinstance(
                longitude, (int, float)
            )
            assert abs(latitude) <= 90 and abs(longitude) <= 180
        except (AssertionError, TypeError):
            return False
        return True

    @property
    def last_updated(self):
        """Return timestamp of last update of weather data."""
        return self._last_updated

    @property
    def current(self):
        """Return current weather data."""
        return self._current

    @property
    def latitude(self):
        """Return weather station latitude."""
        return self._latitude

    @property
    def longitude(self):
        """Return weather station longitude."""
        return self._longitude

    @property
    def attributes(self):
        """Return forecast attributes."""
        return self._attributes

    async def _async_get_data(
        self, url: str, cache_fname=None, max_cache_time=0
    ) -> str:
        """Retreive data from Gismeteo API and cache results."""
        _LOGGER.debug("Requesting URL %s", url)

        data = None
        data_cached = None
        data_is_cached = False

        if self._cache and cache_fname is not None:
            cache_fname += ".xml"
            data_cached = self._cache.read_cache(cache_fname, max_cache_time)
            data_is_cached = self._cache.is_cached(cache_fname)

        if not data_is_cached:
            async with self._session.get(url) as resp:
                if resp.status != HTTPStatus.OK:
                    _LOGGER.error("Invalid response from Gismeteo API: %s", resp.status)
                else:
                    _LOGGER.debug(
                        "Data retrieved from %s, status: %s", url, resp.status
                    )
                    data = await resp.text()

        if not data and data_cached:
            _LOGGER.debug("Cached response used")
            data = data_cached
        elif self._cache and cache_fname is not None and data:
            self._cache.save_cache(cache_fname, data)

        return data

    async def async_get_location(self):
        """Retreive location data from Gismeteo."""
        url = (
            ENDPOINT_URL
            + f"/cities/?lat={self._latitude}&lng={self._longitude}&count=1&lang=en"
        )
        cache_fname = f"location_{self._latitude}_{self._longitude}"

        response = await self._async_get_data(
            url, cache_fname, LOCATION_MAX_CACHE_INTERVAL.total_seconds()
        )
        try:
            xml = etree.fromstring(response)
            item = xml.find("item")
            lon = self._get(item, "lng", float)
            self._attributes = {
                ATTR_ID: self._get(item, "id", int),
                ATTR_NAME: self._get(item, "n"),
            }
            self._latitude = self._get(item, "lat", float)
            self._longitude = (lon - 360) if lon > 180 else lon
        except (etree.ParseError, TypeError, AttributeError) as ex:
            raise ApiError(
                "Can't retrieve location data! Invalid server response."
            ) from ex

    @staticmethod
    def _get(var: dict, ind: str, func: Optional[Callable] = None) -> Any:
        res = var.get(ind)
        if func is not None:
            try:
                res = func(res)
            except (TypeError, ValueError, ArithmeticError):
                return None
        return res

    @staticmethod
    def _is_day(testing_time, sunrise_time, sunset_time):
        """Return True if sun are shining."""
        return sunrise_time < testing_time < sunset_time

    def condition(self, src=None):
        """Return the current condition."""
        src = src or self._current

        cld = src.get(ATTR_WEATHER_CLOUDINESS)
        if cld is None:
            return None
        if cld == 0:
            if self._mode == FORECAST_MODE_DAILY or self._is_day(
                src.get(ATTR_FORECAST_TIME, time.time()),
                src.get(ATTR_SUNRISE),
                src.get(ATTR_SUNSET),
            ):
                cond = ATTR_CONDITION_SUNNY  # Sunshine
            else:
                cond = ATTR_CONDITION_CLEAR_NIGHT  # Clear night
        elif cld == 1:
            cond = ATTR_CONDITION_PARTLYCLOUDY  # A few clouds
        elif cld == 2:
            cond = ATTR_CONDITION_PARTLYCLOUDY  # A some clouds
        else:
            cond = ATTR_CONDITION_CLOUDY  # Many clouds

        pr_type = src.get(ATTR_WEATHER_PRECIPITATION_TYPE)
        pr_int = src.get(ATTR_WEATHER_PRECIPITATION_INTENSITY)
        if src.get(ATTR_WEATHER_STORM):
            cond = ATTR_CONDITION_LIGHTNING  # Lightning/ thunderstorms
            if pr_type != 0:
                cond = (
                    ATTR_CONDITION_LIGHTNING_RAINY  # Lightning/ thunderstorms and rain
                )
        elif pr_type == 1:
            cond = ATTR_CONDITION_RAINY  # Rain
            if pr_int == 3:
                cond = ATTR_CONDITION_POURING  # Pouring rain
        elif pr_type == 2:
            cond = ATTR_CONDITION_SNOWY  # Snow
        elif pr_type == 3:
            cond = ATTR_CONDITION_SNOWY_RAINY  # Snow and Rain
        elif self.wind_speed_ms(src) > 10.8:
            if cond == ATTR_CONDITION_CLOUDY:
                cond = ATTR_CONDITION_WINDY_VARIANT  # Wind and clouds
            else:
                cond = ATTR_CONDITION_WINDY  # Wind
        elif (
            cld == 0
            and src.get(ATTR_WEATHER_PHENOMENON) is not None
            and src.get(ATTR_WEATHER_PHENOMENON) in CONDITION_FOG_CLASSES
        ):
            cond = ATTR_CONDITION_FOG  # Fog

        return cond

    def temperature(self, src=None):
        """Return the current temperature."""
        src = src or self._current
        temperature = src.get(ATTR_WEATHER_TEMPERATURE)
        return float(temperature) if temperature is not None else STATE_UNKNOWN

    def temperature_feels_like(self, src=None):
        """Return the current temperature feeling."""
        temp = self.temperature(src)
        humi = self.humidity(src)
        wind = self.wind_speed_ms(src)
        if STATE_UNKNOWN in (temp, humi, wind):
            return STATE_UNKNOWN

        e_value = humi * 0.06105 * math.exp((17.27 * temp) / (237.7 + temp))
        feels_like = temp + 0.348 * e_value - 0.7 * wind - 4.25
        return round(feels_like, 1)

    def water_temperature(self, src=None):
        """Return the current temperature of water."""
        src = src or self._current
        temperature = src.get(ATTR_WEATHER_WATER_TEMPERATURE)
        return float(temperature) if temperature is not None else STATE_UNKNOWN

    def pressure_mmhg(self, src=None):
        """Return the current pressure in mmHg."""
        src = src or self._current
        pressure = src.get(ATTR_WEATHER_PRESSURE)
        return float(pressure) if pressure is not None else STATE_UNKNOWN

    def pressure_hpa(self, src=None):
        """Return the current pressure in hPa."""
        src = src or self._current
        pressure = src.get(ATTR_WEATHER_PRESSURE)
        return round(pressure * MMHG2HPA, 1) if pressure is not None else STATE_UNKNOWN

    def humidity(self, src=None):
        """Return the name of the sensor."""
        src = src or self._current
        humidity = src.get(ATTR_WEATHER_HUMIDITY)
        return int(humidity) if humidity is not None else STATE_UNKNOWN

    def wind_bearing(self, src=None):
        """Return the current wind bearing."""
        src = src or self._current
        bearing = int(src.get(ATTR_WEATHER_WIND_BEARING, 0))
        return (bearing - 1) * 45 if bearing > 0 else STATE_UNKNOWN

    def wind_speed_kmh(self, src=None):
        """Return the current windspeed in km/h."""
        src = src or self._current
        speed = src.get(ATTR_WEATHER_WIND_SPEED)
        return round(speed * MS2KMH, 1) if speed is not None else STATE_UNKNOWN

    def wind_speed_ms(self, src=None):
        """Return the current windspeed in m/s."""
        src = src or self._current
        speed = src.get(ATTR_WEATHER_WIND_SPEED)
        return float(speed) if speed is not None else STATE_UNKNOWN

    def precipitation_amount(self, src=None):
        """Return the current precipitation amount in mm."""
        src = src or self._current
        precipitation = src.get(ATTR_WEATHER_PRECIPITATION_AMOUNT)
        return precipitation if precipitation is not None else STATE_UNKNOWN

    def forecast(self, src=None):
        """Return the forecast array."""
        src = src or self._forecast
        forecast = []
        now = int(time.time())
        dt_util.set_default_time_zone(self._timezone)
        for i in src:
            fc_time = i.get(ATTR_FORECAST_TIME)
            if fc_time is None:
                continue

            data = {
                ATTR_FORECAST_TIME: dt_util.as_local(
                    datetime.utcfromtimestamp(fc_time)
                ).isoformat(),
                ATTR_FORECAST_CONDITION: self.condition(i),
                ATTR_FORECAST_TEMP: self.temperature(i),
                ATTR_FORECAST_PRESSURE: self.pressure_hpa(i),
                ATTR_FORECAST_HUMIDITY: self.humidity(i),
                ATTR_FORECAST_WIND_SPEED: self.wind_speed_kmh(i),
                ATTR_FORECAST_WIND_BEARING: self.wind_bearing(i),
                ATTR_FORECAST_PRECIPITATION: self.precipitation_amount(i),
            }

            if (
                self._mode == FORECAST_MODE_DAILY
                and i.get(ATTR_FORECAST_TEMP_LOW) is not None
            ):
                data[ATTR_FORECAST_TEMP_LOW] = i.get(ATTR_FORECAST_TEMP_LOW)

            if fc_time < now:
                forecast = [data]
            else:
                forecast.append(data)

        return forecast

    @staticmethod
    def _get_utime(source, tzone):
        local_date = source
        if len(source) <= 10:
            local_date += "T00:00:00"
        tz_h, tz_m = divmod(abs(tzone), 60)
        local_date += f"+{tz_h:02}:{tz_m:02}" if tzone >= 0 else f"-{tz_h:02}:{tz_m:02}"
        return dt_util.as_timestamp(local_date)

    async def async_update(self) -> bool:
        """Get the latest data from Gismeteo."""
        if self.attributes[ATTR_ID] is None:
            await self.async_get_location()

        url = f"{ENDPOINT_URL}/forecast/?city={self.attributes[ATTR_ID]}&lang=en"
        cache_fname = f"forecast_{self.attributes[ATTR_ID]}"

        response = await self._async_get_data(
            url, cache_fname, FORECAST_MAX_CACHE_INTERVAL.total_seconds()
        )
        try:
            xml = etree.fromstring(response)
            tzone = int(xml.find("location").get("tzone"))
            self._attributes[ATTR_LAST_UPDATED] = (
                dt_util.as_local(
                    dt_util.utc_from_timestamp(
                        self._get_utime(xml.find("location").get("cur_time"), tzone)
                    )
                )
                .replace(microsecond=0)
                .isoformat()
            )
            current = xml.find("location/fact")
            current_v = current.find("values")

            self._current = {
                ATTR_SUNRISE: self._get(current, "sunrise", int),
                ATTR_SUNSET: self._get(current, "sunset", int),
                ATTR_WEATHER_CONDITION: self._get(current_v, "descr"),
                ATTR_WEATHER_TEMPERATURE: self._get(current_v, "tflt", float),
                ATTR_WEATHER_PRESSURE: self._get(current_v, "p", int),
                ATTR_WEATHER_HUMIDITY: self._get(current_v, "hum", int),
                ATTR_WEATHER_WIND_SPEED: self._get(current_v, "ws", int),
                ATTR_WEATHER_WIND_BEARING: self._get(current_v, "wd", int),
                ATTR_WEATHER_CLOUDINESS: self._get(current_v, "cl", int),
                ATTR_WEATHER_PRECIPITATION_TYPE: self._get(current_v, "pt", int),
                ATTR_WEATHER_PRECIPITATION_AMOUNT: self._get(current_v, "prflt", float),
                ATTR_WEATHER_PRECIPITATION_INTENSITY: self._get(current_v, "pr", int),
                ATTR_WEATHER_STORM: (self._get(current_v, "ts") == 1),
                ATTR_WEATHER_GEOMAGNETIC_FIELD: self._get(current_v, "grade", int),
                ATTR_WEATHER_PHENOMENON: self._get(current_v, "ph", int),
                ATTR_WEATHER_WATER_TEMPERATURE: self._get(current_v, "water_t", float),
            }

            self._forecast = []
            if self._mode == FORECAST_MODE_HOURLY:
                for day in xml.findall("location/day"):
                    sunrise = self._get(day, "sunrise", int)
                    sunset = self._get(day, "sunset", int)

                    for i in day.findall("forecast"):
                        fc_v = i.find("values")
                        data = {
                            ATTR_SUNRISE: sunrise,
                            ATTR_SUNSET: sunset,
                            ATTR_FORECAST_TIME: self._get_utime(i.get("valid"), tzone),
                            ATTR_FORECAST_CONDITION: self._get(fc_v, "descr"),
                            ATTR_FORECAST_TEMP: self._get(fc_v, "t", int),
                            ATTR_FORECAST_PRESSURE: self._get(fc_v, "p", int),
                            ATTR_FORECAST_HUMIDITY: self._get(fc_v, "hum", int),
                            ATTR_FORECAST_WIND_SPEED: self._get(fc_v, "ws", int),
                            ATTR_FORECAST_WIND_BEARING: self._get(fc_v, "wd", int),
                            ATTR_FORECAST_CLOUDINESS: self._get(fc_v, "cl", int),
                            ATTR_FORECAST_PRECIPITATION_TYPE: self._get(
                                fc_v, "pt", int
                            ),
                            ATTR_FORECAST_PRECIPITATION_AMOUNT: self._get(
                                fc_v, "prflt", float
                            ),
                            ATTR_FORECAST_PRECIPITATION_INTENSITY: self._get(
                                fc_v, "pr", int
                            ),
                            ATTR_FORECAST_STORM: (fc_v.get("ts") == 1),
                            ATTR_FORECAST_GEOMAGNETIC_FIELD: self._get(
                                fc_v, "grade", int
                            ),
                        }
                        self._forecast.append(data)

            else:  # self._mode == FORECAST_MODE_DAILY
                for day in xml.findall("location/day[@descr]"):
                    data = {
                        ATTR_SUNRISE: self._get(day, "sunrise", int),
                        ATTR_SUNSET: self._get(day, "sunset", int),
                        ATTR_FORECAST_TIME: self._get_utime(day.get("date"), tzone),
                        ATTR_FORECAST_CONDITION: self._get(day, "descr"),
                        ATTR_FORECAST_TEMP: self._get(day, "tmax", int),
                        ATTR_FORECAST_TEMP_LOW: self._get(day, "tmin", int),
                        ATTR_FORECAST_PRESSURE: self._get(day, "p", int),
                        ATTR_FORECAST_HUMIDITY: self._get(day, "hum", int),
                        ATTR_FORECAST_WIND_SPEED: self._get(day, "ws", int),
                        ATTR_FORECAST_WIND_BEARING: self._get(day, "wd", int),
                        ATTR_FORECAST_CLOUDINESS: self._get(day, "cl", int),
                        ATTR_FORECAST_PRECIPITATION_TYPE: self._get(day, "pt", int),
                        ATTR_FORECAST_PRECIPITATION_AMOUNT: self._get(
                            day, "prflt", float
                        ),
                        ATTR_FORECAST_PRECIPITATION_INTENSITY: self._get(
                            day, "pr", int
                        ),
                        ATTR_FORECAST_STORM: (self._get(day, "ts") == 1),
                        ATTR_FORECAST_GEOMAGNETIC_FIELD: self._get(
                            day, "grademax", int
                        ),
                    }
                    self._forecast.append(data)

            return True

        except (etree.ParseError, TypeError, AttributeError) as ex:
            raise ApiError(
                "Can't update weather data! Invalid server response."
            ) from ex
