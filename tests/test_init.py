"""Tests for GisMeteo integration."""
from homeassistant.setup import async_setup_component

from custom_components.gismeteo import DOMAIN


async def test_async_setup(hass):
    """Test a successful setup component."""
    await async_setup_component(
        hass,
        DOMAIN,
        {
            "name": "Home",
        },
    )
    await hass.async_block_till_done()


# async def test_async_setup_entry(hass):
#     """Test a successful setup entry."""
#     await init_integration(hass)
#
#     state = hass.states.get("weather.home")
#     assert state is not None
#     assert state.state != STATE_UNAVAILABLE
#     assert state.state == "sunny"
