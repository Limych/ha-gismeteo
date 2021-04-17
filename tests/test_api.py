# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""

from typing import Any, Optional
from unittest.mock import patch

from aiohttp import ClientSession
from asynctest import CoroutineMock
from homeassistant.components.weather import ATTR_WEATHER_WIND_SPEED
from homeassistant.const import ATTR_ID, ATTR_NAME, HTTP_OK, STATE_UNKNOWN
from pytest import raises
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.gismeteo.api import (
    ApiError,
    GismeteoApiClient,
    InvalidCoordinatesError,
)
from custom_components.gismeteo.const import (
    ATTR_WEATHER_CLOUDINESS,
    ATTR_WEATHER_PHENOMENON,
    ATTR_WEATHER_PRECIPITATION_INTENSITY,
    ATTR_WEATHER_PRECIPITATION_TYPE,
    ATTR_WEATHER_STORM,
    CONDITION_FOG_CLASSES,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
)

LATITUDE = 52.0677904
LONGITUDE = 19.4795644
LOCATION_KEY = 3546


async def test__valid_coordinates():
    """Test with valid and invalid location data."""
    lat_valid = (0, 15, 90, -32, -90, LATITUDE)
    lon_valid = (0, 35, 90, 154, 180, -78, -90, -135, -180, LONGITUDE)
    lat_invalid = (90.1, -90.1, 641, -94)
    lon_invalid = (180.1, -180.1, 235, -4566)

    for lat in lat_valid:
        for lon in lon_valid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is True
        for lon in lon_invalid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False
    for lat in lat_invalid:
        for lon in lon_valid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False
        for lon in lon_invalid:
            assert GismeteoApiClient._valid_coordinates(lat, lon) is False

    async with ClientSession() as client:
        with raises(InvalidCoordinatesError):
            GismeteoApiClient(client, latitude=lat_invalid[0], longitude=lon_invalid[0])


async def test__get():
    """Test _get service method."""
    data = {"qwe": 123, "asd": "sdf", "zxc": "789"}

    assert GismeteoApiClient._get(data, "qwe") == 123
    assert GismeteoApiClient._get(data, "asd") == "sdf"
    assert GismeteoApiClient._get(data, "asd", int) is None
    assert GismeteoApiClient._get(data, "zxc") == "789"
    assert GismeteoApiClient._get(data, "zxc") != 789
    assert GismeteoApiClient._get(data, "zxc", int) == 789


@patch("aiohttp.ClientSession.get")
async def test__async_get_data(mock_get):
    """Test with valid location data."""
    mock_get.return_value.__aenter__.return_value.status = HTTP_OK
    mock_get.return_value.__aenter__.return_value.text = CoroutineMock(
        return_value="qwe"
    )
    #
    async with ClientSession() as client:
        gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
        city_id = await gismeteo._async_get_data("some_url")

    assert city_id == "qwe"

    mock_get.return_value.__aenter__.return_value.status = 404
    #
    async with ClientSession() as client:
        gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
        with raises(ApiError):
            await gismeteo._async_get_data("some_url")


async def test_async_get_location():
    """Test with valid location data."""
    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=load_fixture("location.xml"),
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)

            assert gismeteo.attributes[ATTR_ID] is None

            await gismeteo.async_get_location()

    assert gismeteo.attributes[ATTR_ID] == 167413
    assert gismeteo.attributes[ATTR_NAME] == "Razvilka"

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=None,
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
            with raises(ApiError):
                await gismeteo.async_get_location()

    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value="qwe",
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(client, latitude=LATITUDE, longitude=LONGITUDE)
            with raises(ApiError):
                await gismeteo.async_get_location()


def test__get_utime():
    """Test _get_utime service method."""
    assert GismeteoApiClient._get_utime("2021-02-21T16:00:00", 180) == 1613912400
    assert GismeteoApiClient._get_utime("2021-02-21T16:00:00", 0) == 1613923200
    assert GismeteoApiClient._get_utime("2021-02-21", 180) == 1613854800
    assert GismeteoApiClient._get_utime("2021-02-21", 0) == 1613865600

    with raises(ValueError):
        GismeteoApiClient._get_utime("2021-02-", 0)


async def init_gismeteo(
    mode=FORECAST_MODE_HOURLY,
    location_key: Optional[int] = LOCATION_KEY,
    data: Any = False,
):
    """Prepare Gismeteo object."""
    with patch.object(
        GismeteoApiClient,
        "_async_get_data",
        return_value=data if data is not False else load_fixture("forecast.xml"),
    ):
        async with ClientSession() as client:
            gismeteo = GismeteoApiClient(
                client,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                location_key=location_key,
                mode=mode,
                params={
                    "timezone": "UTC",
                },
            )

            assert gismeteo.current == {}

            if location_key is None or data is not False:
                assert await gismeteo.async_update() is False
                assert gismeteo.current == {}
            else:
                assert await gismeteo.async_update() is True
                assert gismeteo.current != {}

    return gismeteo


async def test_api_init():
    """Test data update."""
    gismeteo = await init_gismeteo()

    expected_current = {
        "sunrise": 1613893140,
        "sunset": 1613929620,
        "condition": "Mainly cloudy, light snow",
        "temperature": -7.0,
        "pressure": 746,
        "humidity": 86,
        "wind_speed": 3,
        "wind_bearing": 5,
        "cloudiness": 3,
        "precipitation_type": 2,
        "precipitation_amount": 0.3,
        "precipitation_intensity": 1,
        "storm": False,
        "gm_field": 3,
        "phenomenon": 71,
        "water_temperature": 3.0,
    }

    assert gismeteo.unique_id == f"{LOCATION_KEY}-hourly"
    assert gismeteo.current == expected_current
    assert gismeteo.attributes == {"id": LOCATION_KEY, "name": None}


async def test_async_update():
    """Test data update."""
    gismeteo = await init_gismeteo()

    assert gismeteo.current["cloudiness"] == 3
    assert gismeteo.current["humidity"] == 86
    assert gismeteo.current["phenomenon"] == 71

    with raises(ApiError):
        await init_gismeteo(location_key=None)
    with raises(ApiError):
        await init_gismeteo(data=None)
    with raises(ApiError):
        await init_gismeteo(data="qwe")


async def test_condition():
    """Test condition."""
    gismeteo = await init_gismeteo()

    assert gismeteo.condition() == "snowy"
    assert gismeteo.condition(gismeteo.current) == "snowy"

    gismeteo_d = await init_gismeteo(FORECAST_MODE_DAILY)
    data = gismeteo.current

    data[ATTR_WEATHER_CLOUDINESS] = None
    data[ATTR_WEATHER_PRECIPITATION_TYPE] = 0

    assert gismeteo.condition(data) is None
    assert gismeteo_d.condition(data) is None

    data[ATTR_WEATHER_CLOUDINESS] = 0

    assert gismeteo.condition(data) == "clear-night"
    assert gismeteo_d.condition(data) == "sunny"

    data[ATTR_WEATHER_CLOUDINESS] = 1

    assert gismeteo.condition(data) == "partlycloudy"
    assert gismeteo_d.condition(data) == "partlycloudy"

    data[ATTR_WEATHER_CLOUDINESS] = 2

    assert gismeteo.condition(data) == "partlycloudy"
    assert gismeteo_d.condition(data) == "partlycloudy"

    data[ATTR_WEATHER_CLOUDINESS] = 3

    assert gismeteo.condition(data) == "cloudy"
    assert gismeteo_d.condition(data) == "cloudy"

    data[ATTR_WEATHER_STORM] = True

    assert gismeteo.condition(data) == "lightning"
    assert gismeteo_d.condition(data) == "lightning"

    data[ATTR_WEATHER_PRECIPITATION_TYPE] = 1

    assert gismeteo.condition(data) == "lightning-rainy"
    assert gismeteo_d.condition(data) == "lightning-rainy"

    data[ATTR_WEATHER_STORM] = False

    assert gismeteo.condition(data) == "rainy"
    assert gismeteo_d.condition(data) == "rainy"

    data[ATTR_WEATHER_PRECIPITATION_INTENSITY] = 3

    assert gismeteo.condition(data) == "pouring"
    assert gismeteo_d.condition(data) == "pouring"

    data[ATTR_WEATHER_PRECIPITATION_TYPE] = 3

    assert gismeteo.condition(data) == "snowy-rainy"
    assert gismeteo_d.condition(data) == "snowy-rainy"

    data[ATTR_WEATHER_PRECIPITATION_TYPE] = 0
    data[ATTR_WEATHER_WIND_SPEED] = 11

    assert gismeteo.condition(data) == "windy-variant"
    assert gismeteo_d.condition(data) == "windy-variant"

    data[ATTR_WEATHER_CLOUDINESS] = 0

    assert gismeteo.condition(data) == "windy"
    assert gismeteo_d.condition(data) == "windy"

    data[ATTR_WEATHER_WIND_SPEED] = 0

    for cnd in CONDITION_FOG_CLASSES:
        data[ATTR_WEATHER_PHENOMENON] = cnd

        assert gismeteo.condition(data) == "fog"
        assert gismeteo_d.condition(data) == "fog"


async def test_temperature():
    """Test temperature."""
    gismeteo = await init_gismeteo()

    assert gismeteo.temperature() == -7.0
    assert gismeteo.temperature(gismeteo.current) == -7.0


async def test_temperature_feels_like():
    """Test temperature feels like."""
    gismeteo = await init_gismeteo()

    assert gismeteo.temperature_feels_like() == -12.3
    assert gismeteo.temperature_feels_like(gismeteo.current) == -12.3

    for kind in ["temperature", "humidity", "wind_speed"]:
        with patch.object(gismeteo, kind, return_value=STATE_UNKNOWN):
            assert gismeteo.temperature_feels_like() == STATE_UNKNOWN


async def test_water_temperature():
    """Test temperature of water."""
    gismeteo = await init_gismeteo()

    assert gismeteo.water_temperature() == 3.0
    assert gismeteo.water_temperature(gismeteo.current) == 3.0


async def test_pressure_mmhg():
    """Test pressure in mmHg."""
    gismeteo = await init_gismeteo()

    assert gismeteo.pressure_mmhg() == 746.0
    assert gismeteo.pressure_mmhg(gismeteo.current) == 746.0


async def test_pressure():
    """Test pressure in hPa."""
    gismeteo = await init_gismeteo()

    assert gismeteo.pressure() == 994.6
    assert gismeteo.pressure(gismeteo.current) == 994.6


async def test_humidity():
    """Test humidity."""
    gismeteo = await init_gismeteo()

    assert gismeteo.humidity() == 86
    assert gismeteo.humidity(gismeteo.current) == 86


async def test_wind_bearing():
    """Test wind bearing."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_bearing() == 180
    assert gismeteo.wind_bearing(gismeteo.current) == 180


async def test_wind_speed_kmh():
    """Test wind speed in km/h."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_speed_kmh() == 10.8
    assert gismeteo.wind_speed_kmh(gismeteo.current) == 10.8


async def test_wind_speed():
    """Test wind speed in m/s."""
    gismeteo = await init_gismeteo()

    assert gismeteo.wind_speed() == 3.0
    assert gismeteo.wind_speed(gismeteo.current) == 3.0


async def test_precipitation_amount():
    """Test precipitation amount."""
    gismeteo = await init_gismeteo()

    assert gismeteo.precipitation_amount() == 0.3
    assert gismeteo.precipitation_amount(gismeteo.current) == 0.3


async def test_forecast():
    """Test forecast."""
    with patch(
        "time.time",
        return_value=GismeteoApiClient._get_utime("2021-02-26", 0),
    ):
        gismeteo_d = await init_gismeteo(FORECAST_MODE_DAILY)

        assert gismeteo_d.forecast() == [
            {
                "datetime": "2021-02-25T21:00:00+00:00",
                "condition": "rainy",
                "temperature": 4.0,
                "pressure": 0.0,
                "humidity": 89,
                "wind_speed": 25.2,
                "wind_bearing": 270,
                "precipitation": 0.3,
                "templow": 2,
            },
            {
                "datetime": "2021-02-26T21:00:00+00:00",
                "condition": "cloudy",
                "temperature": 2.0,
                "pressure": 0.0,
                "humidity": 87,
                "wind_speed": 21.6,
                "wind_bearing": 270,
                "precipitation": 0.0,
                "templow": 0,
            },
        ]
