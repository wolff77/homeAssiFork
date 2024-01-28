from enum import Enum

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.area_registry import AreaRegistry
from homeassistant.helpers.device_registry import DeviceRegistry
from homeassistant.helpers.entity import DeviceInfo


class TokenState(Enum):
    unknown = 0
    pending = 1
    approved = 2
    notWorking = 3


class ConnectionState(Enum):
    notConnectedYet = 0
    notReachable = 1
    reachable = 2


class PasswordState(Enum):
    untryed = 0
    wrong = 1
    right = 2


class SensorType(Enum):
    UNDEFINED = -1
    ACTIVE_POWER = 4
    OUTPUT_CURRENT = 5
    ENERGY_METER = 6
    TEMPERATURE_INDOORS = 9
    TEMPERATURE_OUTDOORS = 10
    BRIGHTNESS_INDOORS = 11
    BRIGHTNESS_OUTDOORS = 12
    HUMIDITY_INDOORS = 13
    HUMIDITY_OUTDOORS = 14
    AIR_PRESSURE = 15
    GUST_WIND_SPEED = 16
    GUST_WIND_DIRECTION = 17
    AVERAGE_WIND_SPEED = 18
    AVERAGE_WIND_DIRECTION = 19
    RAIN_VALUE = 20
    CO2_VALUE = 21
    MONOCID_VALUE = 22
    SOUND_PRESSURE = 25
    TARGET_TEMPERATURE = 50
    HEATING_VALVE_VALUE = 51
    OUTPUT_CURRENT_HIGH = 64
    POWER_CONSUMPTION = 65
    GENERIC_TEMPERATURE = 66
    GENERIC_BRIGHTNESS = 67
    GENERIC_HUMIDITY = 68
    GENERATED_POWER = 69
    GENERATED_ENERGY_METER = 70
    WATER_METER = 71
    WATER_FLOW_RATE = 72
    LENGTH = 73
    MASS = 74
    TIME = 75


class AKMType(Enum):
    PRESENCE = 1
    BRIGHTNESS_ZONE = 2
    PRESENCE_DARKNESS = 3
    TWILIGHT = 4
    MOVEMENT = 5
    MOVEMENT_DARKNESS = 6
    SMOKE = 7
    WIND = 8
    RAIN = 9
    SUNLIGHT = 10
    THERMOSTAT = 11
    WINDOW_CONTACT = 13
    DOOR_CONTACT = 14
    WINDOW_HANDLE = 15
    APP = 0


class TemperatureOperationMode(Enum):
    Off = 0
    Heating_Comfort = 1
    Heating_Economy = 2
    Heating_NotUsed = 3
    Heating_Night = 4
    Heating_Holiday = 5
    Cooling_Comfort = 6
    Cooling_off = 7
    Cooling_Economy = 8
    Cooling_NotUsed = 9
    Cooling_Night = 10
    Cooling_Holiday = 11


class HeatingSetting:
    fIsConfigured: bool
    ControlMode: int
    EmergenyValue: int
    CtrlKp: int
    CtrlTa: int
    CtrlTi: int
    CtrlKd: int
    CtrlIMin: float
    CtrlIMax: float
    CtrlYMin: int
    CtrlYMax: int
    CtrlAntiWindUp: bool
    controlDSID: str
    possibleControlDSID: list[str]
    ControlState: int
    IstTemperatur: float
    SollTemperatur: float
    Stellwert: int
    pActiveMode: TemperatureOperationMode
    pTemperatures: dict[TemperatureOperationMode, float]

    def __init__(self, config):
        self.ControlMode = config["ControlMode"]
        self.pActiveMode = TemperatureOperationMode(config["OperationMode"])
        self.IstTemperatur = config["TemperatureValue"]
        self.SollTemperatur = config["NominalValue"]
        self.Stellwert = config["ControlValue"]


class State:
    def __init__(self, name, dsId) -> None:
        self.id = dsId
        self.name = name
        self.nameInactive = "Inaktiv"
        self.nameActive = "Aktiv"
        self.valueActive = "1"
        self.valueAlternativeActive = "active"
        self.valueInactive = "2"
        self.valueAlternativeInactive = "inactive"
        self.dynamicValue = 3


class dSScene:
    name: str
    undoName: str
    id: int
    group: int
    zone: int
    triggerAble: bool
    executeAble: bool
    undoAble: bool
    order: int

    def __init__(self, _id, _group, _zone):
        self.id = _id
        self.group = _group
        self.color_id = _group
        self.zone = _zone
        self.triggerAble = False
        self.executeAble = False
        self.undoAble = False
        self.order = 1000 + _id
        self.trulyExecuteAble = False
        self.defaultName()

    def defaultName(self):
        self.name = "Szene " + str(self.id)

        if self.id == 0:
            self.order = 100
            self.trulyExecuteAble = True
            self.name = "Aus"
            if self.color_id == 4:
                self.name = "Stop"
            if self.color_id == 2:
                self.name = "Schließen"
        if self.id == 1:
            self.order = 120
            self.trulyExecuteAble = True
            self.name = "Bereich 1 Aus"
            if self.group == 48:
                self.name = "Komfort"
            if self.color_id == 4:
                self.name = "Stop"
            if self.color_id == 2:
                self.name = "Bereich 1 schließen"

        if self.id == 2:
            self.order = 130
            self.trulyExecuteAble = True
            self.name = "Bereich 2 Aus"

            if self.group == 48:
                self.name = "Eco"
            if self.color_id == 4:
                self.name = "Stop"
            if self.color_id == 2:
                self.name = "Bereich 1 schließen"

        if self.id == 3:
            self.order = 140
            self.trulyExecuteAble = True
            self.name = "Bereich 3 Aus"

            if self.group == 48:
                self.name = "Raumabsenkung"
            if self.color_id == 4:
                self.name = "Stop"
            if self.color_id == 2:
                self.name = "Bereich 1 schließen"

        if self.id == 4:
            self.order = 150
            self.trulyExecuteAble = True
            self.name = "Bereich 4 Aus"

            if self.group == 48:
                self.name = "Nachtmodus"
            if self.color_id == 4:
                self.name = "Stop"
            if self.color_id == 2:
                self.name = "Bereich 1 schließen"

        if self.id == 5:
            self.order = 110
            self.trulyExecuteAble = True
            self.name = "An"
            if self.group == 48:
                self.name = "Urlaubsmodus"
            if self.color_id == 4:
                self.name = "Start"
            if self.color_id == 2:
                self.name = "Auf"

        if self.id == 6:
            self.order = 121
            self.trulyExecuteAble = True
            self.name = "Bereich 1 An"
            if self.group == 48:
                self.name = "Kühlen"
            if self.color_id == 4:
                self.name = "Start"
            if self.color_id == 2:
                self.name = "Bereich 1 Auf"

        if self.id == 7:
            self.order = 131
            self.trulyExecuteAble = True
            self.name = "Bereich 2 An"
            if self.group == 48:
                self.name = "Kühlen aus"
            if self.color_id == 4:
                self.name = "Start"
            if self.color_id == 2:
                self.name = "Bereich 2 Auf"

        if self.id == 8:
            self.order = 141
            self.trulyExecuteAble = True
            self.name = "Bereich 3 An"
            if self.color_id == 4:
                self.name = "Start"
            if self.color_id == 2:
                self.name = "Bereich 3 Auf"

        if self.id == 9:
            self.order = 151
            self.trulyExecuteAble = True
            self.name = "Bereich 4 An"
            if self.color_id == 4:
                self.name = "Start"
            if self.color_id == 2:
                self.name = "Bereich 4 Auf"

        if self.id == 13:
            self.order = 302
            self.name = "Min"

        if self.id == 14:
            self.order = 301
            self.name = "Max"

        if self.id == 15:
            self.order = 300
            self.name = "Stop"

        if self.id == 17:
            self.order = 111
            self.trulyExecuteAble = True
            self.name = "Szene 2"

        if self.id == 18:
            self.order = 112
            self.trulyExecuteAble = True
            self.name = "Szene 3"
        if self.id == 19:
            self.order = 113
            self.trulyExecuteAble = True
            self.name = "Szene 4"

        if self.id == 20:
            self.order = 122
            self.trulyExecuteAble = True
            self.name = "Szene 1.2"

        if self.id == 21:
            self.order = 123
            self.trulyExecuteAble = True
            self.name = "Szene 1.3"

        if self.id == 22:
            self.order = 124
            self.trulyExecuteAble = True
            self.name = "Szene 1.4"

        if self.id == 23:
            self.order = 132
            self.trulyExecuteAble = True
            self.name = "Szene 2.2"

        if self.id == 24:
            self.order = 133
            self.trulyExecuteAble = True
            self.name = "Szene 2.3"

        if self.id == 25:
            self.order = 134
            self.trulyExecuteAble = True
            self.name = "Szene 2.4"

        if self.id == 26:
            self.order = 142
            self.trulyExecuteAble = True
            self.name = "Szene 3.2"

        if self.id == 27:
            self.order = 143
            self.trulyExecuteAble = True
            self.name = "Szene 3.3"

        if self.id == 28:
            self.order = 144
            self.trulyExecuteAble = True
            self.name = "Szene 3.4"

        if self.id == 29:
            self.order = 152
            self.trulyExecuteAble = True
            self.name = "Szene 4.2"

        if self.id == 30:
            self.order = 153
            self.trulyExecuteAble = True
            self.name = "Szene 4.3"

        if self.id == 31:
            self.order = 154
            self.trulyExecuteAble = True
            self.name = "Szene 4.4"

        if self.id == 32:
            self.order = 120
            self.trulyExecuteAble = True
            self.name = "Szene 1.0"

        if self.id == 33:
            self.order = 121
            self.trulyExecuteAble = True
            self.name = "Szene 1.1"

        if self.id == 34:
            self.order = 130
            self.trulyExecuteAble = True
            self.name = "Szene 2.0"

        if self.id == 35:
            self.order = 131
            self.trulyExecuteAble = True
            self.name = "Szene 2.1"

        if self.id == 36:
            self.order = 140
            self.trulyExecuteAble = True
            self.name = "Szene 3.0"

        if self.id == 37:
            self.order = 141
            self.trulyExecuteAble = True
            self.name = "Szene 3.1"

        if self.id == 38:
            self.order = 150
            self.trulyExecuteAble = True
            self.name = "Szene 4.0"

        if self.id == 39:
            self.order = 151
            self.trulyExecuteAble = True
            self.name = "Szene 4.1"

        if self.id == 50:
            self.order = 200
            self.name = "Lokal aus"

        if self.id == 51:
            self.order = 201
            self.name = "Lokal an"

        if self.id == 56:
            self.order = 400
            self.trulyExecuteAble = True
            self.name = "Sonnenschutz"

        if self.id == 40:
            self.order = 103
            self.trulyExecuteAble = True
            self.name = "Langsam aus"

        if self.id == 41:
            self.order = 100
            self.trulyExecuteAble = True
            self.name = "Impulse"

        if self.id == 64:
            self.name = "Auto aus"

        if self.id == 65:
            self.name = "Panik"
            self.undoName = "Reset Panik"

        if self.id == 67:
            self.order = 101
            self.name = "Standby"

        if self.id == 68:
            self.order = 102
            self.name = "Alles Aus"

        if self.id == 69:
            self.name = "Schlafen"

        if self.id == 70:
            self.name = "Aufstehen"

        if self.id == 71:
            self.name = "Anwesend"

        if self.id == 72:
            self.name = "Abwesend"

        if self.id == 73:
            self.name = "Klingel"

        if self.id == 74:
            self.name = "Alarm 1"
            self.undoName = "Reset Alarm 1"

        if self.id == 76:
            self.name = "Feuer"
            self.undoName = "Reset Feuer"

        if self.id == 83:
            self.name = "Alarm 2"
            self.undoName = "Reset Alarm 2"

        if self.id == 84:
            self.name = "Alarm 3"
            self.undoName = "Reset Alarm 3"

        if self.id == 85:
            self.name = "Alarm 4"
            self.undoName = "Reset Alarm 4"

        if self.id == 88:
            self.name = "Kein Regen"

        if self.id == 89:
            self.name = "Regen"

        if self.id == 90:
            self.name = "Hagel"

        if self.id == 91:
            self.name = "Kein Hagel"


class VDCState:
    def __init__(self, Stateid, name, parent) -> None:
        self.displayName = name
        self.id = Stateid
        self.name = name
        self.parent = parent
        self.dynamicValue = 3


class ZoneState:
    def __init__(self, name, dsId, oZone) -> None:
        self.id = dsId
        self.name = name
        self.nameInactive = "Inaktiv"
        self.nameActive = "Aktiv"
        self.valueActive = "1"
        self.valueAlternativeActive = "active"
        self.valueInactive = "2"
        self.valueAlternativeInactive = "inactive"
        self.pZone = oZone
        self.dynamicValue = 3


class AKMState:
    akmType: AKMType

    def __init__(self, Stateid, oDevice, akmType: AKMType) -> None:
        self.id = Stateid
        self.oDevice = oDevice
        self.akmType = akmType
        self.nameInactive = "Kontakt offen"
        self.nameActive = "Kontakt geschlossen"
        self.valueActive = "1"
        self.valueAlternativeActive = "active"
        self.valueInactive = "2"
        self.valueAlternativeInactive = "inactive"
        self.dynamicValue = 3


class UDA:
    def __init__(self, UDAID, name) -> None:
        self.name = name
        self.id = UDAID


class UDS:
    def __init__(self, UDSID, name, setName, resetName, value, dsType) -> None:
        self.name = name
        self.id = UDSID
        self.value = value
        self.setName = setName
        self.resetName = resetName
        self.dsType = dsType


class dSSensor:
    sensorType: SensorType
    sensorIndex: int

    def __init__(self, sensorType, name, lastValue, valid, sensorIndex) -> None:
        self.sensorType = sensorType
        self.name = name
        self.lastValue = lastValue
        self.valid = valid
        self.hassObject = None
        self.sensorIndex = sensorIndex


class dSDevice:
    groupMembership: list[int]
    sensors: list[dSSensor]
    binaryInputs: dict[int, AKMType]
    pVDCStates: list[VDCState]
    consumptionEvents: dict[str, str]

    def __init__(
        self,
        dSID,
        dSUID,
        name,
        HWInfo,
        present,
        zoneID,
        outputMode,
        functionID,
        hasAction,
        isVdcDevice,
        ean,
        productID,
    ) -> None:
        self.dSID = dSID
        self.dSUID = dSUID
        self.name = name
        self.HWInfo = HWInfo
        self.present = present
        self.zoneID = zoneID
        self.outputMode = outputMode
        self.groupMembership = []
        self.tasterMode = 0
        self.functionID = functionID
        self.baseActionGroup = (functionID >> 12) & 0x0F
        self.hasAction = hasAction
        self.hasVDCStates = False
        self.isVdcDevice = isVdcDevice
        self.sensors = []
        self.hasAKMStates = False
        self.binaryInputs = {}
        self.outputAvaible = outputMode != 0
        self.ean = ean
        self.consumptionEvents = {}
        self.triggerAvaible = False
        self.productID = productID
        self.pVDCStates = []

    def getSensorByType(self, sType: SensorType):
        for sensor in self.sensors:
            if sensor.sensorType == sType:
                return sensor
        return None


class dSGroup:
    devices: list[dSDevice]

    def __init__(self, GroupId, name, zoneID, color_id) -> None:
        self.id = GroupId
        self.name = name
        self.devices = []
        self.zoneID = zoneID
        self.color_id = color_id
        self.scenes = {}
        self.actorAvaible = False
        self.name = "Gruppe " + str(GroupId)
        if GroupId == 0:
            self.name = "Broadcast"
        if GroupId == 1:
            self.name = "Licht"
        if GroupId == 2:
            self.name = "Schatten"
        if GroupId == 3:
            self.name = "Heizung"
        if GroupId == 4:
            self.name = "Audio"
        if GroupId == 5:
            self.name = "Video"
        if GroupId == 6:
            self.name = "Sicherheit"
        if GroupId == 7:
            self.name = "Zugang"
        if GroupId == 8:
            self.name = "Joker"
        if GroupId == 9:
            self.name = "Kühlung"
        if GroupId == 10:
            self.name = "Ventilation"
        if GroupId == 11:
            self.name = "Fenster"
        if GroupId == 48:
            self.name = "Temperaturregelung"
        if GroupId == 64:
            self.name = "Apartmentventilation"


class dSZone:
    groups: list[dSGroup]
    sensoren: list[SensorType]
    devices: list[dSDevice]
    dynamicSensorValue: dict[SensorType, float]
    pHeating: HeatingSetting
    hassID: None

    def __init__(self, ZoneId, name) -> None:
        self.id = ZoneId
        self.name = name
        self.groups = []
        self.devices = []
        self.sensoren = []
        self.dynamicSensorValue = {}
        self.heatingEnabled = False
        self.pHeating = None

    def getSensorValueForType(self, oType: SensorType):
        return self.dynamicSensorValue.get(oType)


class dSCircuit:
    devices: list[dSDevice]

    def __init__(
        self, dSUID, name, DisplayID, busMemberType, fMeteringPossible, hardwareName
    ) -> None:
        self.dSUID = dSUID
        self.name = name
        self.DisplayID = DisplayID
        self.busMemberType = busMemberType
        self.fMeteringPossible = fMeteringPossible
        self.hardwareName = hardwareName
        self.devices = []
        self.sensorWH = 0
        self.sensorW = 0
        self.hassObjectW = None
        self.hassObjectWH = None


class systemStates:
    def __init__(self, name) -> None:
        self.name = name


class zoneStates:
    def __init__(self, name) -> None:
        self.name = name


class dSSConnectionData:
    areareg: AreaRegistry
    devreg: DeviceRegistry
    ipadress = ""
    apptoken = ""
    password = ""
    sessiontoken = None
    passwordState = PasswordState.untryed
    connectionState = ConnectionState.notConnectedYet
    tokenState = TokenState.unknown
    UDAs: list[UDA]
    UDSs: list[UDS]
    zones: list[dSZone]
    devices: list[dSDevice]
    circuits: list[dSCircuit]
    zoneStates: list[ZoneState]
    deviceAKMStates: list[AKMState]
    deviceVDCStates: list[VDCState]
    systemStates: list[State]
    fOldWindowHandling = False
    UDAs = []
    UDSs = []
    zones = []
    devices = []
    circuits = []
    zoneStates = []
    deviceAKMStates = []
    deviceVDCStates = []
    systemStates = []
    myConfig: ConfigEntry

    def getCircuitForId(self, dsuid) -> dSCircuit:
        for circuit in self.circuits:
            if circuit.dSUID == dsuid:
                return circuit
        return None

    def getGroupForID(self, zoneID, groupID) -> dSGroup:
        for zone in self.zones:
            if zone.id == zoneID:
                for group in zone.groups:
                    if group.id == groupID:
                        return group
        return None

    def getSceneForId(self, zoneID, groupID, sceneID) -> dSScene:
        group = self.getGroupForID(zoneID, groupID)
        if group is None:
            return None

        if sceneID not in group.scenes:
            group.scenes[sceneID] = dSScene(sceneID, groupID, zoneID)

        return group.scenes[sceneID]

    def getZoneForID(self, zoneID) -> dSZone:
        for zone in self.zones:
            if zone.id == zoneID:
                return zone
        return None

    def getDevicefromDSUID(self, dsuid) -> dSDevice:
        for device in self.devices:
            if device.dSUID == dsuid:
                return device
        return None

    def getStateByName(self, name) -> State:
        for state in self.deviceAKMStates:
            if state.id == name:
                return state
        for state in self.deviceVDCStates:
            if state.id == name:
                return state
        for state in self.systemStates:
            if state.id == name:
                return state
        for state in self.zoneStates:
            if state.id == name:
                return state
        for state in self.UDSs:
            if state.id == name:
                return state
        return None


class dSMMeterWH(SensorEntity):
    def __init__(self, circuit: dSCircuit) -> None:
        self._dSCiruit = circuit
        self._hass_device_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Energy"

        self._attr_name = circuit.name
        self.entity_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Energy"
        self._attr_unique_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Energy"
        self._attr_native_unit_of_measurement = "Wh"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL
        circuit.hassObjectWH = self

    @property
    def unique_id(self):
        return self._hass_device_id

    @property
    def device_id(self) -> [str, None]:
        return self._hass_device_id

    @property
    def name(self) -> str:
        return self._dSCiruit.name

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id=self.device_id,
            identifiers={("digitalstrom_dss", self._dSCiruit.dSUID + "_Energy")},
            manufacturer="digitalSTROM",
            model=self._dSCiruit.hardwareName,
            name=self._dSCiruit.name,
            sw_version="0.1",
        )

    @property
    def available(self) -> bool:
        return True

    def update(self) -> None:
        self._attr_native_value = self._dSCiruit.sensorWH


class dSMMeterW(SensorEntity):
    def __init__(self, circuit: dSCircuit) -> None:
        self._dSCiruit = circuit
        self._hass_device_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Power"

        self._attr_name = circuit.name
        self.entity_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Power"
        self._attr_unique_id = "digitalstrom_dss." + self._dSCiruit.dSUID + "_Power"
        self._attr_native_unit_of_measurement = "W"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        circuit.hassObjectW = self

    @property
    def unique_id(self):
        return self._hass_device_id

    @property
    def device_id(self) -> [str, None]:
        return self._hass_device_id

    @property
    def name(self) -> str:
        return self._dSCiruit.name

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            config_entry_id=self.device_id,
            identifiers={("digitalstrom_dss", self._dSCiruit.dSUID + "_Power")},
            manufacturer="digitalSTROM",
            model=self._dSCiruit.hardwareName,
            name=self._dSCiruit.name,
            sw_version="0.1",
        )

    @property
    def available(self) -> bool:
        return True

    def update(self) -> None:
        self._attr_native_value = self._dSCiruit.sensorW
