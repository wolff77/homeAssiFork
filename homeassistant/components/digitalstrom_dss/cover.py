"""Platform for light integration."""
from __future__ import annotations

from homeassistant.components.cover import CoverDeviceClass, CoverEntity
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection


class dSGreyDevice(CoverEntity):
    def __init__(self, device) -> None:
        self._dSdevice = device
        self._state = False
        self._attr_current_cover_position = 0
        self._attr_device_class = CoverDeviceClass.BLIND
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_output"
        self._hass_device_id = "digitalstrom_dss." + device.dSUID
        self._attr_is_closed = True
        self._attr_entity_picture = (
            "https://"
            + myConnection.ipadress
            + "/icons/getDeviceIcon?dsuid="
            + device.dSUID
        )

    @property
    def unique_id(self):
        return "digitalstrom_dss." + self._dSdevice.dSUID + "_output"

    @property
    def device_id(self) -> [str, None]:
        """Return the ID of this Hue light."""
        return self._hass_device_id

    @property
    def name(self):
        """Return the name of the luminary."""
        return self._dSdevice.name

    async def async_open_cover(self, **kwargs):
        """Open the cover."""

    async def async_close_cover(self, **kwargs):
        """Close cover."""

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""

    def update(self) -> None:
        return

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
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._dSdevice.present


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
                    if groupIndex == 2:
                        oDevice = dSGreyDevice(device)
                        oDevices.append(oDevice)

    async_add_entities(oDevices)
