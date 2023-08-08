"""The digitalstrom integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry, device_registry
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .dss_connection import *
from .dss_data import *

myConnection: dSSConnectionData = dSSConnectionData()


def searchAndEnable(zoneID, groupID, sceneID):
    oGroup = myConnection.getGroupForID(zoneID, groupID)
    if oGroup is not None:
        if (sceneID in oGroup.scenes) is False:
            oGroup.scenes[sceneID] = {}
        oGroup.scenes[sceneID]["executeAble"] = True
        oGroup.scenes[sceneID]["triggerAble"] = True


def searchAndUndoable(zoneID, groupID, sceneID):
    oGroup = myConnection.getGroupForID(zoneID, groupID)
    if oGroup is not None:
        if (sceneID in oGroup.scenes) is False:
            oGroup.scenes[sceneID] = {}
        oGroup.scenes[sceneID]["undoAble"] = True


def setActorAvaible(zoneID, groupID):
    oGroup = myConnection.getGroupForID(zoneID, groupID)
    if oGroup is not None:
        oGroup.actorAvaible = True


def initVDCDevice(deviceDSUID):
    return


def initHeatingValues():
    return

    response = ajaxSyncRequest(
        myConnection, "/json/apartment/getTemperatureControlStatus", {}, False
    )
    oResultZones = response["zones"]
    for oHeatingKey in oResultZones:
        oHeatingObject = oResultZones[oHeatingKey]
        zoneid = oHeatingObject["id"]
        fConfigured = True
        if "IsConfigured" in oHeatingObject:
            fConfigured = oHeatingObject["IsConfigured"]
        else:
            fConfigured = oHeatingObject["ControlMode"] != 0
        myConnection.getZoneForID(zoneid).heatingEnabled = fConfigured
        myConnection.getZoneForID(zoneid).pHeating = HeatingSetting(oHeatingObject)
    return


def initSystemStateCache():
    response = propertyQuery(
        myConnection,
        "/usr/states/*(*)",
        False,
    )
    for oStateKey in response:
        oStateObject = response[oStateKey]
        name = oStateObject["name"]
        subname = name.split(".")
        fDone = False
        if len(subname) == 3:
            if subname[0] == "zone":
                zoneID = int(subname[1])
                oZone = myConnection.getZoneForID(zoneID)
                if oZone is not None:
                    oState = ZoneState(oZone.name + " " + subname[2], name, oZone)

                    if subname[2] == "presence":
                        oState.name = "Präsenz"
                        oState.nameActive = "präsent"
                        oState.nameInactive = "nicht präsent"
                    elif subname[2] == "motion":
                        oState.name = "Bewegung"
                        oState.nameActive = "Bewegung vorhanden"
                        oState.nameInactive = "keine Bewegung"
                    elif subname[2] == "light":
                        oState.name = "Licht"
                        oState.nameActive = "Hell"
                        oState.nameInactive = "Dunkel"
                    elif subname[2] == "heating":
                        oState.name = "Heizung"
                        oState.nameActive = "Heizung an"
                        oState.nameInactive = "Heizung aus"
                    myConnection.zoneStates.append(oState)
                    fDone = True
        if (len(subname) == 3) and (subname[0] == "dev"):
            oDevice = myConnection.getDevicefromDSUID(subname[1])
            if oDevice is not None:
                if oDevice.hasAKMStates:
                    inputType = 0
                    index = int(subname[2])

                    if index in oDevice.binaryInputs:
                        inputType = oDevice.binaryInputs[index]
                    fSkip = False
                    if myConnection.fOldWindowHandling:
                        if inputType == 13:
                            fSkip = True
                    try:
                        oState = AKMState(name, oDevice, AKMType(inputType))
                        oState.dynamicValue = oStateObject["value"]
                        if inputType == 1:
                            oState.name = "Präsens"
                            oState.nameInactive = "Abwesend"
                            oState.nameActive = "Anwesend"
                        elif inputType == 2:
                            oState.name = "Helligkeit Innen"
                            oState.nameInactive = "Dunkel"
                            oState.nameActive = "Hell"
                        elif inputType == 3:
                            oState.name = "Präsens Nachts"
                            oState.nameInactive = "Abwesend"
                            oState.nameActive = "Anwesend"
                        elif inputType == 4:
                            oState.name = "Dämmerung"
                            oState.nameInactive = "Dunkel"
                            oState.nameActive = "Hell"
                        elif inputType == 5:
                            oState.name = "Bewegung"
                            oState.nameInactive = "keine Bewegung"
                            oState.nameActive = "Bewegung"
                        elif inputType == 6:
                            oState.name = "Bewegung im Dunkel"
                            oState.nameInactive = "keine Bewegung"
                            oState.nameActive = "Bewegung"
                        elif inputType == 7:
                            oState.name = "Rauch"
                            oState.nameInactive = "Kein Rauch"
                            oState.nameActive = "Rauch"
                        elif inputType == 8:
                            oState.name = "Wind"
                            oState.nameInactive = "kein Wind"
                            oState.nameActive = "Wind"
                        elif inputType == 9:
                            oState.name = "Regen"
                            oState.nameInactive = "kein Regen"
                            oState.nameActive = "Regen"
                        elif inputType == 10:
                            oState.name = "Sonnenlicht"
                            oState.nameInactive = "Dunkel"
                            oState.nameActive = "Hell"
                        elif inputType == 11:
                            oState.name = "Thermostat"
                            oState.nameInactive = "Kalt"
                            oState.nameActive = "Warm"
                        elif inputType == 13:
                            oState.name = "Fenster"
                            oState.nameInactive = "Offen"
                            oState.nameActive = "Geschlossen"
                        elif inputType == 14:
                            oState.name = "Tür"
                            oState.nameInactive = "Offen"
                            oState.nameActive = "Geschlossen"
                        elif inputType == 15:
                            oState.name = "Generisch"
                            oState.nameInactive = "Inaktiv"
                            oState.nameActive = "Aktiv"
                        if fSkip is False:
                            myConnection.deviceAKMStates.append(oState)
                    except:
                        oState = None
                if oDevice.hasVDCStates:
                    for state in oDevice.pVDCStates:
                        if state.name == subname[2]:
                            state.dynamicValue = oStateObject["state"]
                            myConnection.deviceVDCStates.append(state)
            fDone = True
        if fDone is False:
            oState = State(name, name)
            if name == "daynight":
                oState.name = "Tag/Nacht"
                oState.nameActive = "Tag"
                oState.nameInactive = "Nacht"
                oState.valueActive = "true"
                oState.valueInactive = "false"
            elif name == "twilight":
                oState.name = "Dämmerung"
                oState.nameActive = "Morgengrauen"
                oState.nameInactive = "Abendrot"
                oState.valueActive = "true"
                oState.valueInactive = "false"
            elif name == "daylight":
                oState.name = "Tageslicht"
                oState.nameActive = "Hell"
                oState.nameInactive = "dunkel"
                oState.valueActive = "true"
                oState.valueInactive = "false"
            elif name == "holiday":
                oState.name = "Anwesenheitssimulation"
                oState.nameActive = "Aktiv"
                oState.nameInactive = "Inaktiv"
                oState.valueActive = "on"
                oState.valueInactive = "off"
            elif name == "presence":
                oState.name = "Anwesenheit"
                oState.nameActive = "Anwesend"
                oState.nameInactive = "Abwesend"
                oState.valueActive = "present"
                oState.valueInactive = "absent"
            elif name == "hibernation":
                oState.name = "Schalfen"
                oState.nameActive = "Wach"
                oState.nameInactive = "Schlagen"
                oState.valueActive = "awake"
                oState.valueInactive = "sleeping"
            elif name == "alarm":
                oState.name = "Alarm"
                oState.nameActive = "Alarm"
                oState.nameInactive = "Kein Alarm"
            elif name == "alarm2":
                oState.name = "Alarm 2"
                oState.nameActive = "Alarm"
                oState.nameInactive = "Kein Alarm"
            elif name == "alarm3":
                oState.name = "Alarm 3"
                oState.nameActive = "Alarm"
                oState.nameInactive = "Kein Alarm"
            elif name == "alarm4":
                oState.name = "Alarm 4"
                oState.nameActive = "Alarm"
                oState.nameInactive = "Kein Alarm"
            elif name == "panic":
                oState.name = "Panik"
                oState.nameActive = "Panik"
                oState.nameInactive = "Keine Panik"
            elif name == "fire":
                oState.name = "Feuer"
                oState.nameActive = "Feuer"
                oState.nameInactive = "Kein Feuer"
            elif name == "rain":
                oState.name = "Regen"
                oState.nameActive = "Regen"
                oState.nameInactive = "Kein Regen"
            elif name == "frost":
                oState.name = "Frost"
                oState.nameActive = "Frost"
                oState.nameInactive = "Kein Frost"
            elif name == "hail":
                oState.name = "Hagel"
                oState.nameActive = "Hagel"
                oState.nameInactive = "Kein Hagel"
            elif name == "wind":
                oState.name = "Wind"
                oState.nameActive = "Wind"
                oState.nameInactive = "Kein Wind"
            elif name == "heating_water_system":
                oState = None
            elif name == "heating_system":
                oState = None
            elif name == "heating_system_mode":
                oState = None
            if oState is not None:
                myConnection.systemStates.append(oState)
    initHeatingValues()


def initDeviceCache():
    response = propertyQuery(
        myConnection,
        "/apartment/zones/zone0/devices/*(DisplayID,dSID,dSUID,name,present,ZoneID,"
        + "outputMode,productID,functionID,functionID,isVdcDevice,hasActions,HWInfo)/*(groupMembership,id,EAN,event0,event1,event2,event3)/*(stateValue,inputType,inputIndex,id,name,valid,value,timestamp,type)",
        False,
    )
    for deviceKey in response:
        deviceObject = response[deviceKey]
        oDevice = dSDevice(
            deviceObject["dSID"],
            deviceObject["dSUID"],
            deviceObject["name"],
            deviceObject["HWInfo"],
            deviceObject["present"],
            deviceObject["ZoneID"],
            deviceObject["outputMode"],
            deviceObject["functionID"],
            deviceObject.get("hasAction", False),
            deviceObject.get("isVdcDevice", False),
            deviceObject["productInfo"]["EAN"],
            deviceObject["productID"],
        )
        if "sensorInputs" in deviceObject:
            oInputs = deviceObject["sensorInputs"]
            for inputID in oInputs:
                pSensorDescription = oInputs[inputID]
                try:
                    oSensor = dSSensor(
                        SensorType(pSensorDescription["type"]),
                        pSensorDescription.get("name", "Name"),
                        pSensorDescription.get("value", ""),
                        pSensorDescription.get("valid", False),
                    )
                    oDevice.sensors.append(oSensor)
                except:
                    oSensor = None
        if "binaryInputs" in deviceObject:
            fMaybeOldWindow13 = False
            fMaybeOldWindow15 = False
            for iInputs in deviceObject["binaryInputs"]:
                oInputs = deviceObject["binaryInputs"][iInputs]
                oDevice.hasAKMStates = True
                inputType = oInputs["inputType"]
                inputIndex = oInputs["inputIndex"]
                if inputType == 13:
                    fMaybeOldWindow13 = True
                if inputType == 15:
                    fMaybeOldWindow15 = True
                oDevice.binaryInputs[inputIndex] = inputType
                if fMaybeOldWindow13:
                    if fMaybeOldWindow15:
                        myConnection.fOldWindowHandling = True
        if "states" in deviceObject:
            for sStateName in deviceObject["states"]:
                oDevice.hasVDCStates = True
                pState = VDCState(
                    "dev." + oDevice.dSUID + "." + sStateName, sStateName, oDevice
                )
                oDevice.pVDCStates.append(pState)
        if "groups" in deviceObject:
            for groupID in deviceObject["groups"]:
                iGroup = deviceObject["groups"][groupID]["id"]
                if oDevice.baseActionGroup == 8:
                    oDevice.baseActionGroup = iGroup
                if oDevice.outputAvaible:
                    setActorAvaible(oDevice.zoneID, iGroup)
                oDevice.groupMembership.append(iGroup)
        if "sensorEvents" in deviceObject:
            for sKey in deviceObject["sensorEvents"]:
                oDevice.consumptionEvents[sKey] = deviceObject["sensorEvents"][sKey]
        activeGroup = deviceObject["button"]["groupMembership"]
        oDevice.tasterMode = deviceObject["button"]["id"]
        if oDevice.tasterMode != 255:
            oDevice.triggerAvaible = True
        else:
            oDevice.triggerAvaible = False
        if (activeGroup != 0) and (activeGroup != 6) and (activeGroup != 7):
            if oDevice.productID == 12488:
                if (oDevice.functionID == 33052) or (oDevice.functionID == 33044):
                    if activeGroup != 8:
                        searchAndEnable(oDevice.zoneID, activeGroup, 0)
                        searchAndEnable(oDevice.zoneID, activeGroup, 5)
                        searchAndEnable(oDevice.zoneID, activeGroup, 17)
                        searchAndEnable(oDevice.zoneID, activeGroup, 18)
                        searchAndEnable(oDevice.zoneID, activeGroup, 19)

            if oDevice.tasterMode > 0:
                if activeGroup == 2:
                    searchAndEnable(oDevice.zoneID, activeGroup, 56)
                    searchAndEnable(oDevice.zoneID, activeGroup, 15)
                if activeGroup == 1:
                    searchAndEnable(oDevice.zoneID, activeGroup, 40)
            if oDevice.tasterMode == 0:
                searchAndEnable(oDevice.zoneID, activeGroup, 0)
                searchAndEnable(oDevice.zoneID, activeGroup, 5)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 1:
                searchAndEnable(oDevice.zoneID, activeGroup, 1)
                searchAndEnable(oDevice.zoneID, activeGroup, 6)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 2:
                searchAndEnable(oDevice.zoneID, activeGroup, 2)
                searchAndEnable(oDevice.zoneID, activeGroup, 7)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 3:
                searchAndEnable(oDevice.zoneID, activeGroup, 3)
                searchAndEnable(oDevice.zoneID, activeGroup, 8)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 4:
                searchAndEnable(oDevice.zoneID, activeGroup, 4)
                searchAndEnable(oDevice.zoneID, activeGroup, 9)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 5:
                searchAndEnable(oDevice.zoneID, activeGroup, 0)
                searchAndEnable(oDevice.zoneID, activeGroup, 5)
                searchAndEnable(oDevice.zoneID, activeGroup, 17)
                searchAndEnable(oDevice.zoneID, activeGroup, 18)
                searchAndEnable(oDevice.zoneID, activeGroup, 19)
            elif oDevice.tasterMode == 6:
                searchAndEnable(oDevice.zoneID, activeGroup, 32)
                searchAndEnable(oDevice.zoneID, activeGroup, 33)
                searchAndEnable(oDevice.zoneID, activeGroup, 20)
                searchAndEnable(oDevice.zoneID, activeGroup, 21)
                searchAndEnable(oDevice.zoneID, activeGroup, 22)
            elif oDevice.tasterMode == 7:
                searchAndEnable(oDevice.zoneID, activeGroup, 34)
                searchAndEnable(oDevice.zoneID, activeGroup, 35)
                searchAndEnable(oDevice.zoneID, activeGroup, 23)
                searchAndEnable(oDevice.zoneID, activeGroup, 24)
                searchAndEnable(oDevice.zoneID, activeGroup, 25)
            elif oDevice.tasterMode == 8:
                searchAndEnable(oDevice.zoneID, activeGroup, 36)
                searchAndEnable(oDevice.zoneID, activeGroup, 37)
                searchAndEnable(oDevice.zoneID, activeGroup, 26)
                searchAndEnable(oDevice.zoneID, activeGroup, 27)
                searchAndEnable(oDevice.zoneID, activeGroup, 28)
            elif oDevice.tasterMode == 9:
                searchAndEnable(oDevice.zoneID, activeGroup, 38)
                searchAndEnable(oDevice.zoneID, activeGroup, 39)
                searchAndEnable(oDevice.zoneID, activeGroup, 29)
                searchAndEnable(oDevice.zoneID, activeGroup, 30)
                searchAndEnable(oDevice.zoneID, activeGroup, 31)
            elif oDevice.tasterMode == 10:
                searchAndEnable(oDevice.zoneID, activeGroup, 1)
                searchAndEnable(oDevice.zoneID, activeGroup, 6)
                searchAndEnable(oDevice.zoneID, activeGroup, 20)
                searchAndEnable(oDevice.zoneID, activeGroup, 21)
                searchAndEnable(oDevice.zoneID, activeGroup, 22)
            elif oDevice.tasterMode == 11:
                searchAndEnable(oDevice.zoneID, activeGroup, 2)
                searchAndEnable(oDevice.zoneID, activeGroup, 7)
                searchAndEnable(oDevice.zoneID, activeGroup, 23)
                searchAndEnable(oDevice.zoneID, activeGroup, 24)
                searchAndEnable(oDevice.zoneID, activeGroup, 25)
            elif oDevice.tasterMode == 12:
                searchAndEnable(oDevice.zoneID, activeGroup, 3)
                searchAndEnable(oDevice.zoneID, activeGroup, 8)
                searchAndEnable(oDevice.zoneID, activeGroup, 26)
                searchAndEnable(oDevice.zoneID, activeGroup, 27)
                searchAndEnable(oDevice.zoneID, activeGroup, 28)
            elif oDevice.tasterMode == 13:
                searchAndEnable(oDevice.zoneID, activeGroup, 4)
                searchAndEnable(oDevice.zoneID, activeGroup, 9)
                searchAndEnable(oDevice.zoneID, activeGroup, 29)
                searchAndEnable(oDevice.zoneID, activeGroup, 30)
                searchAndEnable(oDevice.zoneID, activeGroup, 31)
        if oDevice.functionID == 0x7010:
            searchAndEnable(0, 0, 73)
        if oDevice.functionID == 0x6001:
            searchAndEnable(0, 0, 65)
        if oDevice.functionID == 0x7050:
            searchAndEnable(0, 0, 71)
            searchAndEnable(0, 0, 72)
        myConnection.devices.append(oDevice)
        if oDevice.hasVDCStates or oDevice.hasAction:
            initVDCDevice(oDevice)
    initSystemStateCache()


def initdSMCache():
    response = propertyQuery(
        myConnection,
        "/apartment/dSMeters/*(dSUID,name,busMemberType,DisplayID)/capabilities(metering)",
        False,
    )
    for dsmKey in response:
        dsmObject = response[dsmKey]
        dSUID = dsmObject["dSUID"]
        name = dsmObject["name"]
        DisplayId = dsmObject["DisplayID"]
        busMemberType = dsmObject["busMemberType"]
        fMeteringPossible = False
        if "capabilities" in dsmObject:
            if "metering" in dsmObject["capabilities"]:
                fMeteringPossible = dsmObject["capabilities"]["metering"]
        dsm = dSCircuit(dSUID, name, DisplayId, busMemberType, fMeteringPossible)
        myConnection.circuits.append(dsm)
    initDeviceCache()


def initZoneSensorCache():
    response = propertyQuery(
        myConnection,
        "/apartment/zones/*(ZoneID)/groups/group0/sensor/*(type,value)",
        False,
    )
    for zoneKey in response:
        zoneObject = response[zoneKey]
        pZone: dSZone
        pZone = myConnection.getZoneForID(zoneObject["ZoneID"])
        if pZone is not None:
            for sensorKey in zoneObject:
                if sensorKey != "ZoneID":
                    sensorObject = zoneObject[sensorKey]
                    type = sensorObject["type"]
                    value = sensorObject["value"]
                    try:
                        pType = SensorType(type)
                        pZone.sensoren.append(pType)
                        pZone.dynamicSensorValue[pType] = value
                    except:
                        pType = None
    initdSMCache()


def initZoneCache():
    response = propertyQuery(
        myConnection,
        "/apartment/zones/*(ZoneID,name)/groups/*(group,name,color,connectedDevices)/scenes/*(scene,name)",
        False,
    )
    for zoneKey in response:
        zone = response[zoneKey]
        if zone["ZoneID"] is not None:
            newZone = dSZone(zone["ZoneID"], zone["name"])
            if zone["ZoneID"] == 0:
                newZone.name = "Ganzes Apartment"
            myConnection.zones.append(newZone)
        for groupKey in zone:
            if groupKey != "ZoneID":
                if groupKey != "name":
                    group: dict
                    group = zone[groupKey]
                    newGroup = dSGroup(
                        group["group"],
                        group.get("name"),
                        zone["ZoneID"],
                        group["color"],
                    )
                    newZone.groups.append(newGroup)
                    for sceneKey in group:
                        if sceneKey != "name":
                            if sceneKey != "group":
                                if sceneKey != "color":
                                    if sceneKey != "connectedDevices":
                                        scene = group[sceneKey].get("scene", None)
                                        name = group[sceneKey].get("name", None)
                                        if scene is not None:
                                            if (scene in newGroup.scenes) is False:
                                                newGroup.scenes[scene] = {}
                                            newGroup.scenes[scene]["name"] = name
                    if group["connectedDevices"] is not None:
                        if group["connectedDevices"] > 0:
                            searchAndEnable(newGroup.zoneID, newGroup.id, 0)
                            searchAndEnable(newGroup.zoneID, newGroup.id, 5)
                            searchAndEnable(newGroup.zoneID, newGroup.id, 17)
                            searchAndEnable(newGroup.zoneID, newGroup.id, 18)
                            searchAndEnable(newGroup.zoneID, newGroup.id, 19)
                            searchAndEnable(0, 0, 67)

    searchAndEnable(0, 0, 68)
    searchAndEnable(0, 0, 69)
    searchAndEnable(0, 0, 70)
    searchAndEnable(0, 0, 90)
    searchAndEnable(0, 0, 91)

    searchAndUndoable(0, 0, 65)
    searchAndUndoable(0, 0, 76)
    searchAndUndoable(0, 0, 74)
    searchAndUndoable(0, 0, 83)
    searchAndUndoable(0, 0, 84)
    searchAndUndoable(0, 0, 85)

    oZone = myConnection.getZoneForID(0)
    for oGroup in oZone.groups:
        if oGroup.id > 15:
            if oGroup.id > 48:
                if len(oGroup.name) > 0:
                    searchAndEnable(0, oGroup.id, 0)
                    searchAndEnable(0, oGroup.id, 5)
                    searchAndEnable(0, oGroup.id, 17)
                    searchAndEnable(0, oGroup.id, 18)
                    searchAndEnable(0, oGroup.id, 19)
    initZoneSensorCache()


def loadInstallation():
    return


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("dSS_IP"): cv.string,
                vol.Optional("application_token"): cv.string,
                vol.Optional("dSS_Password"): cv.string,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass, config_entry):
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    ip = config[DOMAIN].get("dSS_IP", "")
    password = config[DOMAIN].get("dSS_Password", "")
    myConnection.ipadress = ip
    myConnection.password = password
    if config[DOMAIN].get("application_token", "") == "":
        fetchAppToken(myConnection)
    else:
        myConnection.apptoken = config[DOMAIN].get("application_token")

    await hass.async_add_executor_job(initZoneCache)

    myConnection.devreg = device_registry.async_get(hass)
    myConnection.areareg = area_registry.async_get(hass)

    for oZone in myConnection.zones:
        oZone.hassID = myConnection.areareg.async_get_or_create(oZone.name).id

    return True
