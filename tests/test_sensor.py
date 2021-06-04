# pylint: disable=protected-access,redefined-outer-name
"""Tests for Gismeteo integration."""

from asynctest import Mock, patch
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_MONITORED_CONDITIONS,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant

from custom_components.gismeteo import GismeteoDataUpdateCoordinator
from custom_components.gismeteo.const import ATTRIBUTION
from custom_components.gismeteo.sensor import GismeteoSensor, _fix_kinds, _gen_entities

from tests.const import FAKE_UNIQUE_ID


async def test__fix_kinds(caplog):
    """Test fix_kinds function."""
    caplog.clear()
    res = _fix_kinds([])
    assert res == []
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_kinds(["qwe", "asd"])
    assert res == []
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_kinds(["humidity", "temperature"])
    assert res == ["temperature", "humidity"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_kinds(
        ["humidity", "temperature", "pressure", "forecast", "pressure_mmhg"]
    )
    assert res == ["temperature", "humidity", "pressure"]
    assert len(caplog.records) == 0

    caplog.clear()
    res = _fix_kinds(["humidity", "temperature", "weather"])
    assert res == ["condition", "temperature", "humidity"]
    assert len(caplog.records) == 1

    caplog.clear()
    res = _fix_kinds(["humidity", "temperature", "weather"], False)
    assert res == ["condition", "temperature", "humidity"]
    assert len(caplog.records) == 0


@patch("custom_components.gismeteo.GismeteoDataUpdateCoordinator")
async def test__gen_entities(mock_coordinator):
    """Test _gen_entities function."""
    res = _gen_entities("Test location", mock_coordinator, {}, False)
    assert len(res) == 14

    res = _gen_entities(
        "Test location",
        mock_coordinator,
        {CONF_MONITORED_CONDITIONS: ["temperature", "humidity"]},
        False,
    )
    assert len(res) == 2


async def test_entity_initialization(hass: HomeAssistant):
    """Test entity initialization."""
    mock_api = Mock()
    mock_api.temperature = Mock(return_value="asd")
    mock_api.attributes = {}

    coordinator = GismeteoDataUpdateCoordinator(hass, FAKE_UNIQUE_ID, mock_api)
    sensor = GismeteoSensor("Test", "temperature", coordinator)

    expected_attributes = {
        ATTR_ATTRIBUTION: ATTRIBUTION,
    }

    assert sensor.name == "Test Temperature"
    assert sensor.unique_id == f"{FAKE_UNIQUE_ID}-temperature"
    assert sensor.should_poll is False
    assert sensor.available is True
    assert sensor.state == "asd"
    assert sensor.unit_of_measurement == TEMP_CELSIUS
    assert sensor.icon is None
    assert sensor.device_class == DEVICE_CLASS_TEMPERATURE
    assert sensor.device_state_attributes == expected_attributes
