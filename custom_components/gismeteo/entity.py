#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import GismeteoDataUpdateCoordinator
from .api import GismeteoApiClient
from .const import ATTRIBUTION, DOMAIN, NAME


class GismeteoEntity(CoordinatorEntity):
    """Gismeteo entity."""

    def __init__(self, name: str, coordinator: GismeteoDataUpdateCoordinator):
        """Class initialization."""
        super().__init__(coordinator)
        self._name = name

    @property
    def _gismeteo(self) -> GismeteoApiClient:
        return self.coordinator.gismeteo

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self._gismeteo.location_key)},
            "name": NAME,
            "entry_type": "service",
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
