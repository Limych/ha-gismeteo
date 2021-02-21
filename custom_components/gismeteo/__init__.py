#
#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import logging

from homeassistant.core import Config, HomeAssistant

_LOGGER = logging.getLogger(__name__)


# Base component constants
DOMAIN = "gismeteo"
VERSION = "dev"
ISSUE_URL = "https://github.com/Limych/ha-gismeteo/issues"
ATTRIBUTION = "Data provided by Gismeteo"


# pylint: disable=unused-argument
async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up component."""
    # Print startup message
    _LOGGER.info("Version %s", VERSION)
    _LOGGER.info(
        "If you have ANY issues with this, please report them here: %s", ISSUE_URL
    )

    hass.data.setdefault(DOMAIN, {})
    return True
