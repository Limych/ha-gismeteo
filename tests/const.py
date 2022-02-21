"""Constants for tests."""
from typing import Final

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

MOCK_UNIQUE_ID: Final = "test_id"

MOCK_CONFIG: Final = {
    CONF_NAME: "Home",
    CONF_LATITUDE: 55.55,
    CONF_LONGITUDE: 122.12,
}
