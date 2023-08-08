from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.helpers.entity import DeviceInfo

from .. import myConnection
from ..dss_connection import ajaxSyncRequest
from ..dss_data import dSDevice


class dSLightActorDimmer(LightEntity):
    def __init__(self, device: dSDevice) -> None:
        self._dSdevice = device
        self._state = False
        self._brightness = 0
        self._attr_supported_color_modes = set()
        self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)
        self._attr_supported_features |= LightEntityFeature.TRANSITION
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_output"
        self._hass_device_id = "digitalstrom_dss." + device.dSUID

    @property
    def unique_id(self):
        return "digitalstrom_dss." + self._dSdevice.dSUID + "_output"

    @property
    def device_id(self) -> [str, None]:
        """Return the ID of this Hue light."""
        return self._hass_device_id

    # "digitalstrom_dss." + self._dSdevice.dSUID

    @property
    def color_mode(self) -> str:
        return ColorMode.BRIGHTNESS

    @property
    def _color_mode(self):
        return ColorMode.BRIGHTNESS

    @property
    def brightness(self):
        return self._brightness

    @property
    def name(self):
        """Return the name of the luminary."""
        return self._dSdevice.name

    def turn_on(self, **kwargs):
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        ajaxSyncRequest(
            myConnection,
            "device/setValue",
            {"dsuid": self._dSdevice.dSUID, "value": self._brightness},
            False,
        )
        if self._brightness == 0:
            self._state = False
        else:
            self._state = True

    def turn_off(self):
        """Instruct the light to turn off."""
        ajaxSyncRequest(
            myConnection, "device/turnOff", {"dsuid": self._dSdevice.dSUID}, False
        )
        self._state = False

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
    def is_on(self):
        """Return True if the device is on."""
        return self._brightness > 0

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
