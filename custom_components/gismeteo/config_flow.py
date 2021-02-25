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
import asyncio

from aiohttp import ClientConnectorError, ClientError
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_MODE, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.storage import STORAGE_DIR
import voluptuous as vol

from . import DOMAIN  # pylint: disable=unused-import
from .const import (
    CONF_CACHE_DIR,
    CONF_FORECAST,
    FORECAST_MODE_DAILY,
    FORECAST_MODE_HOURLY,
    UPDATE_INTERVAL,
)
from .gismeteo import ApiError, Gismeteo


class GismeteoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gismeteo."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_import(self, platform_config):
        """Handle import."""
        return await self.async_step_user(platform_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            websession = async_get_clientsession(self.hass)
            cache_dir = user_input.get(
                CONF_CACHE_DIR, self.hass.config.path(STORAGE_DIR)
            )
            try:
                async with timeout(10):
                    gismeteo = Gismeteo(
                        websession,
                        latitude=user_input.get(
                            CONF_LATITUDE, self.hass.config.latitude
                        ),
                        longitude=user_input.get(
                            CONF_LONGITUDE, self.hass.config.longitude
                        ),
                        mode=user_input.get(CONF_MODE, FORECAST_MODE_HOURLY),
                        params={
                            "timezone": str(self.hass.config.time_zone),
                            "cache_dir": cache_dir,
                            "cache_time": UPDATE_INTERVAL.total_seconds(),
                        },
                    )
                    await gismeteo.async_update()
            except (ApiError, ClientConnectorError, asyncio.TimeoutError, ClientError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    gismeteo.location_key, raise_on_progress=False
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
