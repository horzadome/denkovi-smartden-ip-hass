"""Config flow for Denkovi smartDEN IP Devices."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_MODEL,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MODEL_IP16R_ID,
    SUPPORTED_MODELS,
)
from .coordinator import DenkoviCoordinator
from .api import DenkoviApiError, DenkoviClient


class CannotConnect(HomeAssistantError):
    """Error to indicate that connection failed."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate that authentication failed."""


class DenkoviConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Denkovi smartDEN IP Devices."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            model = user_input[CONF_MODEL]
            port = user_input[CONF_PORT]
            try:
                await self.async_set_unique_id(f"{host.lower()}:{port}:{model}")
                self._abort_if_unique_id_configured()
                client = DenkoviClient(
                    self.hass,
                    host=host,
                    port=port,
                    password=user_input[CONF_PASSWORD],
                    model=model,
                )
                await client.async_get_data()
            except DenkoviApiError as err:
                errors["base"] = "cannot_connect"
            except (OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"{SUPPORTED_MODELS[model]} ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_MODEL: model,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    int, vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_PASSWORD): str,
                vol.Required(
                    CONF_MODEL, default=MODEL_IP16R_ID
                ): vol.In(SUPPORTED_MODELS),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(int, vol.Range(min=10, max=300)),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return DenkoviOptionsFlow(config_entry)


class DenkoviOptionsFlow(config_entries.OptionsFlow):
    """Manage integration options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage polling interval."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current
                ): vol.All(int, vol.Range(min=10, max=300))
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
