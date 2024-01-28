from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection
from .dss_data import SensorType, dSDevice, dSMMeterW, dSMMeterWH


class SensorBase(SensorEntity):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID

    @property
    def unique_id(self):
        return (
            "digitalstrom_dss." + self._dSdevice.dSUID + "_sensor" + self._dSSensorIndex
        )

    @property
    def device_id(self) -> [str, None]:
        """Return the ID of this Hue light."""
        return self._hass_device_id

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
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._dSdevice.present

    def update(self) -> None:
        for sensor in self._dSdevice.sensors:
            if sensor.sensorType == self._dSSensorType:
                self._attr_native_value = sensor.lastValue


class TemperaturSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = TEMP_CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class HumiditySensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class BrightnessSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "lx"
        self._attr_device_class = SensorDeviceClass.ILLUMINANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class WindSpeedSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "m/s"
        self._attr_device_class = SensorDeviceClass.WIND_SPEED
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class RainSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "mm/m2"
        self._attr_device_class = SensorDeviceClass.PRECIPITATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class COSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_device_class = SensorDeviceClass.CO
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class CO2Sensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_device_class = SensorDeviceClass.CO2
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class SoundPressureSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "dB"
        self._attr_device_class = SensorDeviceClass.SOUND_PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class PowerSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "W"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class AirPressureSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "hPa"
        self._attr_device_class = SensorDeviceClass.ATMOSPHERIC_PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class CurrentSensor(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "mA"
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class EnergyMeterSensorKwh(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "kWh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


class EnergyMeterSensorWh(SensorBase):
    def __init__(
        self, device: dSDevice, sensorType: SensorType, sensorIndex: int
    ) -> None:
        self._dSdevice = device
        self._attr_name = device.name
        self._dSSensorType = sensorType
        self._dSSensorIndex = sensorIndex
        self.entity_id = "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        self._attr_unique_id = (
            "digitalstrom_dss." + device.dSUID + "_sensor" + sensorIndex
        )
        self._attr_native_unit_of_measurement = "Wh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._hass_device_id = "digitalstrom_dss." + self._dSdevice.dSUID


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig

    for circuit in myConnection.circuits:
        if circuit.fMeteringPossible:
            oDevices.append(dSMMeterW(circuit))
            oDevices.append(dSMMeterWH(circuit))

    for device in myConnection.devices:
        if device.present:
            for sensor in device.sensors:
                if sensor.valid:
                    if (
                        sensor.sensorType == SensorType.TEMPERATURE_INDOORS
                        or sensor.sensorType == SensorType.TEMPERATURE_OUTDOORS
                        or sensor.sensorType == SensorType.GENERIC_TEMPERATURE
                        or sensor.sensorType == SensorType.TARGET_TEMPERATURE
                    ):
                        tempSensor = TemperaturSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if (
                        sensor.sensorType == SensorType.HUMIDITY_INDOORS
                        or sensor.sensorType == SensorType.HUMIDITY_OUTDOORS
                        or sensor.sensorType == SensorType.GENERIC_HUMIDITY
                    ):
                        tempSensor = HumiditySensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if (
                        sensor.sensorType == SensorType.BRIGHTNESS_INDOORS
                        or sensor.sensorType == SensorType.BRIGHTNESS_OUTDOORS
                        or sensor.sensorType == SensorType.GENERIC_BRIGHTNESS
                    ):
                        tempSensor = BrightnessSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if (
                        sensor.sensorType == SensorType.AVERAGE_WIND_SPEED
                        or sensor.sensorType == SensorType.GUST_WIND_SPEED
                    ):
                        tempSensor = WindSpeedSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if sensor.sensorType == SensorType.RAIN_VALUE:
                        tempSensor = RainSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if sensor.sensorType == SensorType.CO2_VALUE:
                        tempSensor = CO2Sensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if sensor.sensorType == SensorType.MONOCID_VALUE:
                        tempSensor = COSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if sensor.sensorType == SensorType.SOUND_PRESSURE:
                        tempSensor = SoundPressureSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if (
                        sensor.sensorType == SensorType.ACTIVE_POWER
                        or sensor.sensorType == SensorType.GENERATED_POWER
                        or sensor.sensorType == SensorType.POWER_CONSUMPTION
                    ):
                        tempSensor = PowerSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if sensor.sensorType == SensorType.AIR_PRESSURE:
                        tempSensor = AirPressureSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

                    if (
                        sensor.sensorType == SensorType.OUTPUT_CURRENT
                        or sensor.sensorType == SensorType.OUTPUT_CURRENT_HIGH
                    ):
                        tempSensor = CurrentSensor(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)
                    if sensor.sensorType == SensorType.ENERGY_METER:
                        tempSensor = EnergyMeterSensorKwh(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)
                    if sensor.sensorType == SensorType.GENERATED_ENERGY_METER:
                        tempSensor = EnergyMeterSensorWh(
                            device, sensor.sensorType, sensor.sensorIndex
                        )
                        sensor.hassObject = tempSensor
                        oDevices.append(tempSensor)

    #    GUST_WIND_DIRECTION = 17 degrees
    #    AVERAGE_WIND_DIRECTION = 19 degrees
    #    HEATING_VALVE_VALUE = 51 percent
    #    WATER_METER = 71 l
    #    WATER_FLOW_RATE = 72 l/s
    #    LENGTH = 73 m
    #    MASS = 74 gra
    #    TIME = 75 s

    async_add_entities(oDevices)
