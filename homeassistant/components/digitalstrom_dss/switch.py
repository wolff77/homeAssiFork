from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection
from .dss_data import dSDevice


class JokerDevice(SwitchEntity):
    def __init__(self, device: dSDevice) -> None:
        self._dSdevice = device
        self._state = False
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_output"
        self._hass_device_id = "digitalstrom_dss." + device.dSUID
        self._attr_entity_picture = (
            "https://"
            + myConnection.ipadress
            + "/icons/getDeviceIcon?dsuid="
            + device.dSUID
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id=self.device_id,
            identifiers={("digitalstrom_dss", self._dSdevice.dSUID)},
            manufacturer="digitalSTROM",
            model=self._dSdevice.HWInfo,
            name=self._dSdevice.name,
            sw_version="0.1",
            suggested_area=myConnection.getZoneForID(self._dSdevice.zoneID).name,
        )

    @property
    def unique_id(self):
        return "digitalstrom_dss." + self._dSdevice.dSUID + "_output"

    @property
    def device_id(self) -> [str, None]:
        """Return the ID of this Hue light."""
        return self._hass_device_id

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""

    @property
    def name(self):
        """Return the name of the luminary."""
        return self._dSdevice.name

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._dSdevice.present

    @property
    def is_on(self) -> bool | None:
        return False


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    for device in myConnection.devices:
        if device.present:
            if device.outputAvaible:
                if device.baseActionGroup == 8:
                    device = JokerDevice(device)
                    oDevices.append(device)
    async_add_entities(oDevices)
