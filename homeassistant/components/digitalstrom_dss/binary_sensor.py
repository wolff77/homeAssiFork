from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection
from .dss_data import AKMType


class dSBinarySensor(BinarySensorEntity):
    def __init__(self, device, index) -> None:
        self._dSdevice = device
        self._dSIndex = index
        self._dSState = "dev." + device.dSUID + "." + str(index)
        self.internalState = myConnection.getStateByName(self._dSState)
        self._hass_device_id = "digitalstrom_dss." + device.dSUID
        self._attr_unique_id = "digitalstrom_dss." + device.dSUID + str(self._dSIndex)
        self._state = None
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_" + str(self._dSIndex)
        if self.internalState is not None:
            if self.internalState.dynamicValue == 1:
                self._state = True
            else:
                if self.internalState.dynamicValue == 2:
                    self._state = False

    @property
    def name(self) -> str:
        return self._dSdevice.name

    @property
    def unique_id(self):
        return "digitalstrom_dss." + self._dSdevice.dSUID + "_" + str(self._dSIndex)

    @property
    def device_id(self) -> [str, None]:
        return self._hass_device_id

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

    async def async_update(self):
        if self.internalState is None:
            self._state = None
        else:
            if self.internalState.dynamicValue == 1:
                self._state = True
            else:
                if self.internalState.dynamicValue == 2:
                    self._state = False

    @property
    def is_on(self) -> bool | None:
        if self.internalState is None:
            self._state = None
            return None
        if self.internalState.dynamicValue == 1:
            self._state = True
            return True
        if self.internalState.dynamicValue == 2:
            self._state = False
            return False
        return None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._dSdevice.present


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    devices = []
    for device in myConnection.devices:
        for binaryInputKey in device.binaryInputs:
            dSType = device.binaryInputs[binaryInputKey]
            if (dSType == AKMType.MOVEMENT) or (dSType == AKMType.MOVEMENT_DARKNESS):
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.MOTION
                devices.append(binDevice)
            if dSType == AKMType.BRIGHTNESS_ZONE:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.LIGHT
                devices.append(binDevice)
            if dSType in [
                AKMType.DOOR_CONTACT,
                AKMType.WINDOW_CONTACT,
                AKMType.WINDOW_HANDLE,
            ]:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.DOOR
                devices.append(binDevice)
            if (dSType == AKMType.PRESENCE) or (dSType == AKMType.PRESENCE_DARKNESS):
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.PRESENCE
                devices.append(binDevice)
            if dSType == AKMType.RAIN:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.MOISTURE
                devices.append(binDevice)
            if dSType == AKMType.SMOKE:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.SMOKE
                devices.append(binDevice)
            if dSType == AKMType.SUNLIGHT:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.LIGHT
                devices.append(binDevice)
            if dSType == AKMType.TWILIGHT:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.LIGHT
                devices.append(binDevice)
            if dSType == AKMType.THERMOSTAT:
                binDevice = dSBinarySensor(device, binaryInputKey)
                binDevice._attr_device_class = BinarySensorDeviceClass.HEAT
                devices.append(binDevice)

    async_add_entities(devices)
