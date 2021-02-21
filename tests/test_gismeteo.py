#
#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
Tests for the Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from unittest.mock import patch

from aiohttp import ClientSession
from asynctest import CoroutineMock
from pytest import raises
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.gismeteo.const import HTTP_OK
from custom_components.gismeteo.gismeteo import (
    ApiError,
    Gismeteo,
    InvalidCoordinatesError,
)

LATITUDE = 52.0677904
LONGITUDE = 19.4795644


# pylint: disable=protected-access
async def test__valid_coordinates():
    """Test with valid and invalid location data."""
    lat_valid = (0, 15, 90, -32, -90, LATITUDE)
    lon_valid = (0, 35, 90, 154, 180, -78, -90, -135, -180, LONGITUDE)
    lat_invalid = (90.1, -90.1, 641, -94)
    lon_invalid = (180.1, -180.1, 235, -4566)

    for lat in lat_valid:
        for lon in lon_valid:
            assert Gismeteo._valid_coordinates(lat, lon) is True
        for lon in lon_invalid:
            assert Gismeteo._valid_coordinates(lat, lon) is False
    for lat in lat_invalid:
        for lon in lon_valid:
            assert Gismeteo._valid_coordinates(lat, lon) is False
        for lon in lon_invalid:
            assert Gismeteo._valid_coordinates(lat, lon) is False

    async with ClientSession() as client:
        with raises(InvalidCoordinatesError):
            Gismeteo(client, latitude=lat_invalid[0], longitude=lon_invalid[0])


# pylint: disable=protected-access
def test__get():
    """Test _get service method."""
    data = {"qwe": 123, "asd": "sdf", "zxc": "789"}

    assert Gismeteo._get(data, "qwe") == 123
    assert Gismeteo._get(data, "asd") == "sdf"
    assert Gismeteo._get(data, "asd", int) is None
    assert Gismeteo._get(data, "zxc") == "789"
    assert Gismeteo._get(data, "zxc") != 789
    assert Gismeteo._get(data, "zxc", int) == 789


@patch("aiohttp.ClientSession.get")
# pylint: disable=protected-access
async def test__async_get_data(mock_get):
    """Test with valid location data."""
    mock_get.return_value.__aenter__.return_value.status = HTTP_OK
    mock_get.return_value.__aenter__.return_value.text = CoroutineMock(
        return_value="qwe"
    )

    async with ClientSession() as client:
        gismeteo = Gismeteo(client, latitude=LATITUDE, longitude=LONGITUDE)
        city_id = await gismeteo._async_get_data("some_url")

    assert city_id == "qwe"

    mock_get.return_value.__aenter__.return_value.status = 404

    async with ClientSession() as client:
        gismeteo = Gismeteo(client, latitude=LATITUDE, longitude=LONGITUDE)
        with raises(ApiError):
            await gismeteo._async_get_data("some_url")


# pylint: disable=protected-access
async def test__async_get_nearest_city_id():
    """Test with valid location data."""
    city_location = load_fixture("city_location.xml")

    with patch(
        "custom_components.gismeteo.gismeteo.Gismeteo._async_get_data",
        return_value=city_location,
    ):
        async with ClientSession() as client:
            gismeteo = Gismeteo(client, latitude=LATITUDE, longitude=LONGITUDE)
            city_id = await gismeteo._async_get_nearest_city_id()

    assert city_id == 167413


# pylint: disable=protected-access
def test__get_utime():
    """Test _get_utime service method."""
    assert Gismeteo._get_utime("2021-02-21T16:00:00", 180) == 1613912400
    assert Gismeteo._get_utime("2021-02-21T16:00:00", 0) == 1613923200


async def get_gismeteo():
    """Prepare Gismeteo object."""
    forecast_data = load_fixture("forecast_data.xml")

    with patch(
        "custom_components.gismeteo.gismeteo.Gismeteo._async_get_nearest_city_id",
        return_value=6572,
    ), patch(
        "custom_components.gismeteo.gismeteo.Gismeteo._async_get_data",
        return_value=forecast_data,
    ):
        async with ClientSession() as client:
            gismeteo = Gismeteo(client, latitude=LATITUDE, longitude=LONGITUDE)

            assert gismeteo.current == {}
            assert await gismeteo.async_update() is True
            assert gismeteo.current != {}

    return gismeteo


async def test_async_update():
    """Test data update."""
    gismeteo = await get_gismeteo()

    assert gismeteo.current["cloudiness"] == 3
    assert gismeteo.current["humidity"] == 86
    assert gismeteo.current["phenomenon"] == 71


async def test_condition():
    """Test current condition."""
    gismeteo = await get_gismeteo()

    assert gismeteo.condition() == "snowy"
    assert gismeteo.condition(gismeteo.current) == "snowy"


async def test_temperature():
    """Test current temperature."""
    gismeteo = await get_gismeteo()

    assert gismeteo.temperature() == -7.0
    assert gismeteo.temperature(gismeteo.current) == -7.0


async def test_pressure_mmhg():
    """Test current pressure in mmHg."""
    gismeteo = await get_gismeteo()

    assert gismeteo.pressure_mmhg() == 746.0
    assert gismeteo.pressure_mmhg(gismeteo.current) == 746.0


async def test_pressure_hpa():
    """Test current pressure in hPa."""
    gismeteo = await get_gismeteo()

    assert gismeteo.pressure_hpa() == 994.6
    assert gismeteo.pressure_hpa(gismeteo.current) == 994.6


async def test_humidity():
    """Test current humidity."""
    gismeteo = await get_gismeteo()

    assert gismeteo.humidity() == 86
    assert gismeteo.humidity(gismeteo.current) == 86


async def test_wind_bearing():
    """Test current wind bearing."""
    gismeteo = await get_gismeteo()

    assert gismeteo.wind_bearing() == 180
    assert gismeteo.wind_bearing(gismeteo.current) == 180


async def test_wind_speed_kmh():
    """Test current wind speed in km/h."""
    gismeteo = await get_gismeteo()

    assert gismeteo.wind_speed_kmh() == 10.8
    assert gismeteo.wind_speed_kmh(gismeteo.current) == 10.8


async def test_wind_speed_ms():
    """Test current wind speed in m/s."""
    gismeteo = await get_gismeteo()

    assert gismeteo.wind_speed_ms() == 3.0
    assert gismeteo.wind_speed_ms(gismeteo.current) == 3.0


async def test_precipitation_amount():
    """Test current precipitation amount."""
    gismeteo = await get_gismeteo()

    assert gismeteo.precipitation_amount() == 0.3
    assert gismeteo.precipitation_amount(gismeteo.current) == 0.3


# def test_forecast():
#     self.fail()
