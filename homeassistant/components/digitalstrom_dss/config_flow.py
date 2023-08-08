"""Config flow for digitalstrom integration."""
from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, info):
        return self.async_create_entry(title="dssconfig", data={})
