from enum import Enum

from homeassistant.helpers.area_registry import AreaRegistry
from homeassistant.helpers.device_registry import DeviceRegistry


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
    def __init__(self, UDSID, name) -> None:
        self.name = name
        self.id = UDSID
        self.value = ""


class dSSensor:
    sensorType: SensorType

    def __init__(self, sensorType, name, lastValue, valid) -> None:
        self.sensorType = sensorType
        self.name = name
        self.lastValue = lastValue
        self.valid = valid


class dSDevice:
    groupMembership: list[int]
    sensors: list[dSSensor]
    binaryInputs: dict[int, int]
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


class dSCircuit:
    devices: list[dSDevice]

    def __init__(
        self, dSUID, name, DisplayID, busMemberType, fMeteringPossible
    ) -> None:
        self.dSUID = dSUID
        self.name = name
        self.DisplayID = DisplayID
        self.busMemberType = busMemberType
        self.fMeteringPossible = fMeteringPossible
        self.devices = []


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
    zones: list[dSZone]
    devices: list[dSDevice]
    circuits: list[dSCircuit]
    zoneStates: list[ZoneState]
    deviceAKMStates: list[AKMState]
    deviceVDCStates: list[VDCState]
    systemStates: list[State]
    fOldWindowHandling = False
    UDAs = []
    zones = []
    devices = []
    circuits = []
    zoneStates = []
    deviceAKMStates = []
    deviceVDCStates = []
    systemStates = []

    def getGroupForID(self, zoneID, groupID) -> dSGroup:
        for zone in dSSConnectionData.zones:
            if zone.id == zoneID:
                for group in zone.groups:
                    if group.id == groupID:
                        return group
        return None

    def getZoneForID(self, zoneID) -> dSZone:
        for zone in dSSConnectionData.zones:
            if zone.id == zoneID:
                return zone
        return None

    def getDevicefromDSUID(self, dsuid) -> dSDevice:
        for device in dSSConnectionData.devices:
            if device.dSUID == dsuid:
                return device
        return None
