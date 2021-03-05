#  Copyright (c) 2019-2021, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons BY-NC-SA 4.0 International Public License
#  (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
"""
The Gismeteo component.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-gismeteo/
"""

import asyncio
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from aiohttp import ClientConnectorError, ClientError
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_MODE, CONF_NAME

from . import DOMAIN, get_gismeteo  # pylint: disable=unused-import
from .api import ApiError
from .const import (
    CONF_FORECAST,
    CONF_PLATFORMS,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
)

_LOGGER = logging.getLogger(__name__)


class GismeteoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gismeteo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(self, platform_config):
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data=platform_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            platforms = user_input.get(CONF_PLATFORMS, [SENSOR_DOMAIN, WEATHER_DOMAIN])
            user_input[CONF_PLATFORMS] = platforms

            try:
                async with timeout(10):
                    gismeteo = get_gismeteo(self.hass, user_input)
                    await gismeteo.async_update()
            except (ApiError, ClientConnectorError, asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    gismeteo.unique_id, raise_on_progress=False
                )

                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LATITUDE, default=self.hass.config.latitude
                    ): cv.latitude,
                    vol.Optional(
                        CONF_LONGITUDE, default=self.hass.config.longitude
                    ): cv.longitude,
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Optional(
                        CONF_FORECAST,
                        default=self.hass.config.get(CONF_FORECAST, False),
                    ): bool,
                    vol.Optional(CONF_MODE, default=FORECAST_MODE_HOURLY): vol.In(
                        [FORECAST_MODE_HOURLY, FORECAST_MODE_DAILY]
                    ),
                }
            ),
            errors=errors,
        )
