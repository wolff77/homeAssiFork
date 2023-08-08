"""Platform for light integration."""
from __future__ import annotations

from . import myConnection
from .devices.dSLightActorDimmer import dSLightActorDimmer
from .devices.dSLightActorSwitch import dSLightActorSwitch


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
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
    for oDevice in oDevices:
        oDevice.forceDeviceEntry()
    # Add devices
