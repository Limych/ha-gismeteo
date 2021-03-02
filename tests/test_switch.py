"""Test integration_blueprint switch."""
from unittest.mock import call, patch

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.integration_blueprint import async_setup_entry
from custom_components.integration_blueprint.const import DEFAULT_NAME, DOMAIN, SWITCH

from .const import MOCK_CONFIG


async def test_switch_services(hass):
    """Test switch services."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    assert await async_setup_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Functions/objects can be patched directly in test code as well and can be used to test
    # additional things, like whether a function was called or what arguments it was called with
    with patch(
        "custom_components.integration_blueprint.IntegrationBlueprintApiClient.async_set_title"
    ) as title_func:
        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_OFF,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        assert title_func.called
        assert title_func.call_args == call("foo")

        title_func.reset_mock()

        await hass.services.async_call(
            SWITCH,
            SERVICE_TURN_ON,
            service_data={ATTR_ENTITY_ID: f"{SWITCH}.{DEFAULT_NAME}_{SWITCH}"},
            blocking=True,
        )
        assert title_func.called
        assert title_func.call_args == call("bar")
