from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import myConnection
from .dss_connection import executeUDA
from .dss_data import UDA


class UdaButton(ButtonEntity):
    udaid = ""

    def __init__(self, uda: UDA) -> None:
        self._attr_name = uda.name
        self._attr_unique_id = "digitalstrom_dss.uda_" + uda.id
        self.udaid = uda.id

    def press(self) -> None:
        executeUDA(myConnection, self.udaid)

    @property
    def device_id(self) -> [str, None]:
        return "virtual_control_0"

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id="virtual_control_0",
            identifiers={("digitalstrom_dss", "virtual_control_0")},
            manufacturer="digitalSTROM",
            model="Virtual Control Container for digitalSTROM Zone",
            name=myConnection.getZoneForID(0).name,
            sw_version="0.1",
            suggested_area=myConnection.getZoneForID(0).name,
        )


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    udaButtons = []
    for uda in myConnection.UDAs:
        udaButton = UdaButton(uda)
        udaButtons.append(udaButton)
    add_entities(udaButtons)
