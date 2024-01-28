"""Platform for light integration."""
from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    const,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection
from .dss_data import SensorType, dSZone


class Heating(ClimateEntity):
    def __init__(self, zone: dSZone) -> None:
        self.dsZone = zone
        self._attr_current_temperature = zone.getSensorValueForType(
            SensorType.TEMPERATURE_INDOORS
        )
        self._attr_target_temperature = zone.getSensorValueForType(
            SensorType.TARGET_TEMPERATURE
        )
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_preset_mode = ""
        self._attr_preset_modes = [
            const.PRESET_COMFORT,
            const.PRESET_ECO,
            const.PRESET_AWAY,
            const.PRESET_SLEEP,
        ]
        self._attr_hvac_modes = []
        self._attr_hvac_mode = None

    @property
    def unique_id(self):
        return "digitalstrom_dss." + str(self.dsZone.id) + "_heating"

    @property
    def device_id(self) -> [str, None]:
        return "virtual_control_" + str(self.dsZone.id)

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id="virtual_control_" + str(self.dsZone.id),
            identifiers={
                ("digitalstrom_dss", "virtual_control_" + str(self.dsZone.id))
            },
            manufacturer="digitalSTROM",
            model="Virtual Control Container for digitalSTROM Zone",
            name=self.dsZone.name,
            sw_version="0.1",
            suggested_area=myConnection.getZoneForID(self.dsZone.id).name,
        )

    @property
    def name(self):
        return "Temperaturregelung " + self.dsZone.name

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""

    async def async_update(self):
        self._attr_current_temperature = self.dsZone.getSensorValueForType(
            SensorType.TEMPERATURE_INDOORS
        )
        self._attr_target_temperature = self.dsZone.getSensorValueForType(
            SensorType.TARGET_TEMPERATURE
        )


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    for zone in myConnection.zones:
        if zone.heatingEnabled:
            heatingDev = Heating(zone)
            oDevices.append(heatingDev)
    async_add_entities(oDevices)
