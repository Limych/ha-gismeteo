"""Constants for tests."""

from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SENSORS,
)

from custom_components.gismeteo.const import (
    CONF_PLATFORM_FORMAT,
    CONF_WEATHER,
    SENSOR,
    WEATHER,
)

MOCK_UNIQUE_ID = "test_id"

MOCK_CONFIG = {
    CONF_NAME: "Home",
    CONF_LATITUDE: 55.55,
    CONF_LONGITUDE: 122.12,
}

MOCK_CONFIG_OPTIONS = {
    CONF_PLATFORM_FORMAT.format(WEATHER): True,
    CONF_PLATFORM_FORMAT.format(SENSOR): True,
}

MOCK_CONFIG_YAML = {
    "home": {
        CONF_NAME: "Home",
        CONF_LATITUDE: 55.55,
        CONF_LONGITUDE: 122.12,
        CONF_WEATHER: {},
        CONF_SENSORS: {CONF_MONITORED_CONDITIONS: ["condition"]},
    },
}
