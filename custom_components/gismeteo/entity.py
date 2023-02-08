#  Copyright (c) 2019-2022, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""
from typing import Any, Dict, Optional

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_ID,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    CONF_SHOW_ON_MAP,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GismeteoDataUpdateCoordinator
from .api import GismeteoApiClient
from .const import ATTR_LAT, ATTR_LON, ATTRIBUTION, DOMAIN, NAME


class GismeteoEntity(CoordinatorEntity):
    """Gismeteo entity."""

    def __init__(
        self,
        location_name: str,
        coordinator: GismeteoDataUpdateCoordinator,
        config: dict,
    ):
        """Class initialization."""
        super().__init__(coordinator)
        self._location_name = location_name
        self._config = config

    @property
    def _gismeteo(self) -> GismeteoApiClient:
        return self.coordinator.gismeteo

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._gismeteo.attributes[ATTR_ID])},
            "name": NAME,
            "manufacturer": NAME,
            "model": "Forecast",
        }

    @property
    def extra_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the state attributes."""
        attrs = self._gismeteo.attributes.copy()

        if self._config.get(CONF_SHOW_ON_MAP, False):
            attrs[ATTR_LATITUDE] = self._gismeteo.latitude
            attrs[ATTR_LONGITUDE] = self._gismeteo.longitude
        else:
            attrs[ATTR_LAT] = self._gismeteo.latitude
            attrs[ATTR_LON] = self._gismeteo.longitude

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION

        return attrs
