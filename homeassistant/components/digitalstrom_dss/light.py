"""Platform for light integration."""
from __future__ import annotations

from homeassistant.helpers import entity_platform

from . import myConnection
from .devices.dSLightActorDimmer import dSLightActorDimmer
from .devices.dSLightActorSwitch import dSLightActorSwitch


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    for device in myConnection.devices:
        if device.present:
            if device.outputAvaible:
                for groupIndex in device.groupMembership:
                    if groupIndex == 1:
                        oDevice = None
                        if device.outputMode == 16:
                            oDevice = dSLightActorSwitch(device)
                        else:
                            oDevice = dSLightActorDimmer(device)
                        oDevices.append(oDevice)

    async_add_entities(oDevices)

    # Add devices
