from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.helpers.entity import DeviceInfo

from .. import myConnection
from ..dss_connection import ajaxSyncRequest
from ..dss_data import dSDevice


class dSLightActorSwitch(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, device: dSDevice) -> None:
        """Initialize an AwesomeLight."""
        self._dSdevice = device
        self._state = False
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_output"
        self._attr_unique_id = "digitalstrom_dss." + device.dSUID + "_output"
        self._attr_supported_color_modes = [ColorMode.ONOFF]
        self._attr_supported_features |= LightEntityFeature.TRANSITION
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID

    @property
    def unique_id(self):
        return "digitalstrom_dss." + self._dSdevice.dSUID + "_output"

    @property
    def device_id(self) -> [str, None]:
        """Return the ID of this Hue light."""
        return self._hass_device_id

    @property
    def color_mode(self) -> str:
        return ColorMode.ONOFF

    @property
    def _color_mode(self):
        return ColorMode.ONOFF

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._dSdevice.name

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
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self) -> None:
        ajaxSyncRequest(
            myConnection, "device/turnOn", {"dsuid": self._dSdevice.dSUID}, False
        )
        self._state = True

    def turn_off(self) -> None:
        """Instruct the light to turn off."""
        ajaxSyncRequest(
            myConnection, "device/turnOff", {"dsuid": self._dSdevice.dSUID}, False
        )
        self._state = False

    def update(self) -> None:
        return

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._dSdevice.present

    def forceDeviceEntry(self):
        dev = myConnection.devreg.async_get_or_create(
            config_entry_id=self.device_id,
            identifiers={("digitalstrom_dss", self._dSdevice.dSUID)},
            manufacturer="digitalSTROM",
            model=self._dSdevice.HWInfo,
            name=self._dSdevice.name,
            sw_version="0.1",
            suggested_area=myConnection.getZoneForID(self._dSdevice.zoneID).name,
        )
        self._hass_device_id = dev.id
