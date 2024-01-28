"""Config flow for digitalstrom integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from . import myConnection
from .const import DOMAIN
from .dss_connection import fetchAppToken


@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input) -> FlowResult:
        await self.async_set_unique_id("digitalSTROM.dss")
        # self._abort_if_unique_id_configured()
        if user_input is not None:
            if user_input["password"] is not None:
                if user_input["host"] is not None:
                    myConnection.ipadress = user_input["host"]
                    myConnection.password = user_input["password"]
                    if await fetchAppToken(myConnection):
                        await self.async_set_unique_id("digitalstrom.dssConnections")
                        return self.async_create_entry(
                            title="dSS Verbindung",
                            data={
                                "appToken": myConnection.apptoken,
                                "host": myConnection.ipadress,
                            },
                        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("host"): str, vol.Required("password"): str}
            ),
        )
