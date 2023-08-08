from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import myConnection
from .dss_connection import executeUDA, fetchUDA
from .dss_data import UDA


class UdaButton(ButtonEntity):
    udaid = ""

    def __init__(self, uda: UDA) -> None:
        self._attr_name = uda.name
        self._attr_unique_id = "digitalstrom.uda_" + uda.id
        self.udaid = uda.id

    def press(self) -> None:
        executeUDA(myConnection, self.udaid)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    fetchUDA(myConnection, False)

    udaButtons = []
    for uda in myConnection.UDAs:
        udaButton = UdaButton(uda)
        udaButtons.append(udaButton)
    add_entities(udaButtons)
