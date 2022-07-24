"""Constants for tests."""
from typing import Final

from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME

MOCK_UNIQUE_ID: Final = "test_id"
MOCK_API_ID: Final = "test_api_id"

MOCK_LATITUDE: Final = 55.55
MOCK_LONGITUDE: Final = 122.12

MOCK_CONFIG: Final = {
    CONF_NAME: "Home",
    CONF_LATITUDE: MOCK_LATITUDE,
    CONF_LONGITUDE: MOCK_LONGITUDE,
}
