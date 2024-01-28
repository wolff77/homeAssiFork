from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo

from . import myConnection
from .dss_data import UDS, dSGroup


class SceneControl(SelectEntity):
    def __init__(self, oGroup: dSGroup) -> None:
        self.dSGroup = oGroup
        selects = []
        for scene in oGroup.scenes:
            if oGroup.scenes[scene].executeAble is True:
                selects.append(oGroup.scenes[scene])
        sorted(selects, key=lambda obj: obj.order)
        content = []
        for select in selects:
            content.append(select.name)
        self._attr_options = content
        self._attr_current_option = content[0]

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

    @property
    def name(self):
        return self.dSGroup.name

    @property
    def device_id(self) -> [str, None]:
        return "virtual_control_" + str(self.dSGroup.zoneID)

    @property
    def unique_id(self):
        return (
            "digitalstrom_dss.scene_"
            + str(self.dSGroup.zoneID)
            + "_"
            + str(self.dSGroup.id)
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id="virtual_control_" + str(self.dSGroup.zoneID),
            identifiers={
                ("digitalstrom_dss", "virtual_control_" + str(self.dSGroup.zoneID))
            },
            manufacturer="digitalSTROM",
            model="Virtual Control Container for digitalSTROM Zone",
            name=myConnection.getZoneForID(self.dSGroup.zoneID).name,
            sw_version="0.1",
            suggested_area=myConnection.getZoneForID(self.dSGroup.zoneID).name,
        )


class UDSSelect(SelectEntity):
    # Implement one of these methods.

    def __init__(self, oUDS: UDS) -> None:
        self.dSUDS = oUDS
        # self._attr_name = oUDS.name
        # self.entity_id = "digitalstrom_dss.uds_" + oUDS.id
        self._attr_options = [oUDS.setName, oUDS.resetName]
        if oUDS.value == 1:
            self._attr_current_option = oUDS.setName
        else:
            self._attr_current_option = oUDS.resetName

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

    @property
    def name(self):
        return self.dSUDS.name

    @property
    def device_id(self) -> [str, None]:
        return "virtual_control_0"

    @property
    def unique_id(self):
        return "digitalstrom_dss.uds_" + str(self.dSUDS.id)

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
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
) -> None:
    oDevices = []
    platform = entity_platform.async_get_current_platform()
    platform.config_entry = myConnection.myConfig
    for oUDS in myConnection.UDSs:
        if oUDS.dsType == "custom-states":
            pObj = UDSSelect(oUDS)
            oDevices.append(pObj)

    for oZone in myConnection.zones:
        for oGroup in oZone.groups:
            fShouldAdd = False
            for scene in oGroup.scenes:
                if oGroup.scenes[scene].executeAble is True:
                    fShouldAdd = True
            if fShouldAdd:
                pObj = SceneControl(oGroup)
                oDevices.append(pObj)

    async_add_entities(oDevices)
