#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging
from typing import Any, Dict, List, Optional

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from . import GismeteoDataUpdateCoordinator, _convert_yaml_config
from .const import (
    ATTRIBUTION,
    CONF_PLATFORM_FORMAT,
    COORDINATOR,
    DOMAIN,
    DOMAIN_YAML,
    SENSOR,
    SENSOR_TYPES,
)
from .entity import GismeteoEntity

_LOGGER = logging.getLogger(__name__)


def _fix_kinds(kinds: List[str], warn=True) -> List[str]:
    """Remove unwanted values from kinds."""
    kinds = set(kinds)

    for kind in ["forecast", "pressure_mmhg", "weather"]:
        if kind in kinds:
            kinds.remove(kind)

            if kind == "weather":
                kinds = kinds | {"condition"}
                if warn:
                    _LOGGER.warning(
                        'The "weather" condition is deprecated,'
                        ' please replace it with "condition"'
                    )

    return [x for x in SENSOR_TYPES if x in kinds]


def _gen_entities(
    location_name: str,
    coordinator: GismeteoDataUpdateCoordinator,
    config: ConfigType,
    warn: bool,
):
    """Generate entities."""
    entities = []

    _LOGGER.debug(config)
    for kind in _fix_kinds(
        config.get(CONF_MONITORED_CONDITIONS, SENSOR_TYPES.keys()),
        warn=warn,
    ):
        entities.append(GismeteoSensor(location_name, kind, coordinator))
        if kind == "pressure":
            entities.append(GismeteoSensor(location_name, "pressure_mmhg", coordinator))

    return entities


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Add Gismeteo sensor entities."""
    entities = []
    if config_entry.source == SOURCE_IMPORT:
        # Setup from configuration.yaml
        for uid, cfg in hass.data[DOMAIN_YAML].items():
            cfg = _convert_yaml_config(cfg)

            if cfg.get(CONF_PLATFORM_FORMAT.format(SENSOR), False) is False:
                continue  # pragma: no cover

            location_name = cfg[CONF_NAME]
            coordinator = hass.data[DOMAIN][uid][COORDINATOR]

            entities.extend(_gen_entities(location_name, coordinator, cfg, True))

    else:
        # Setup from config entry
        config = config_entry.data.copy()  # type: ConfigType
        config.update(config_entry.options)

        if config.get(CONF_PLATFORM_FORMAT.format(SENSOR), False) is False:
            return  # pragma: no cover

        location_name = config[CONF_NAME]
        coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

        entities.extend(_gen_entities(location_name, coordinator, config, False))

    async_add_entities(entities, False)


class GismeteoSensor(GismeteoEntity):
    """Implementation of an Gismeteo sensor."""

    def __init__(
        self,
        location_name: str,
        kind: str,
        coordinator: GismeteoDataUpdateCoordinator,
    ):
        """Initialize the sensor."""
        super().__init__(location_name, coordinator)

        self._kind = kind

    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        return f"{self._gismeteo.unique_id}-{self._kind}".lower()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._location_name} {SENSOR_TYPES[self._kind][ATTR_NAME]}"

    @property
    def state(self):
        """Return the state."""
        try:
            return getattr(self._gismeteo, self._kind)()

        except KeyError:  # pragma: no cover
            _LOGGER.warning("Condition is currently not available: %s", self._kind)
            return None

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement of this entity, if any."""
        return SENSOR_TYPES[self._kind].get(ATTR_UNIT_OF_MEASUREMENT)

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return SENSOR_TYPES[self._kind].get(ATTR_ICON)

    @property
    def device_class(self) -> Optional[str]:
        """Return the device_class."""
        return SENSOR_TYPES[self._kind].get(ATTR_DEVICE_CLASS)

    @property
    def device_state_attributes(self) -> Optional[Dict[str, Any]]:
        """Return the state attributes."""
        attrs = self._gismeteo.attributes.copy()
        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attrs
