from asyncio import sleep
import json
import ssl
import urllib.parse

import httpx
import requests
import urllib3
import websockets

from homeassistant.core import HomeAssistant

urllib3.disable_warnings()

from .dss_data import (
    ConnectionState,
    PasswordState,
    SensorType,
    TokenState,
    dSSConnectionData,
)


async def onMessage(message: str, pObject: dSSConnectionData):
    msgObj = json.loads(message)
    if ("name" in msgObj) is False:
        return
    print(msgObj["name"])
    if msgObj["name"] == "stateChange":
        pState = pObject.getStateByName(msgObj["properties"]["statename"])
        if pState is not None:
            pState.dynamicValue = msgObj["properties"]["value"]
    if msgObj["name"] == "addonStateChange":
        if msgObj["source"]["serviceName"] == "system-addon-user-defined-states":
            pState = pObject.getStateByName(msgObj["properties"]["statename"])
            if pState is not None:
                pState.dynamicValue = msgObj["properties"]["value"]
    if msgObj["name"] == "callScene":
        if msgObj["source"]["isDevice"]:
            device = pObject.getDevicefromDSUID(msgObj["source"]["dsid"])
            msgObj["properties"]["sceneID"]
        if msgObj["source"]["isGroup"]:
            pObject.getGroupForID(
                msgObj["source"]["zoneID"], msgObj["source"]["groupID"]
            )
            msgObj["properties"]["sceneID"]
    if msgObj["name"] == "zoneSensorValue":
        zone = pObject.getZoneForID(msgObj["source"]["zoneID"])
        if int(msgObj["properties"]["sensorType"]) in [
            x.value for x in SensorType._member_map_.values()
        ]:
            pType = SensorType(int(msgObj["properties"]["sensorType"]))
            zone.dynamicSensorValue[pType] = float(
                msgObj["properties"]["sensorValueFloat"]
            )
    if msgObj["name"] == "deviceSensorValue":
        device = pObject.getDevicefromDSUID(msgObj["source"]["dsid"])
        if int(msgObj["properties"]["sensorType"]) in [
            x.value for x in SensorType._member_map_.values()
        ]:
            pType = SensorType(int(msgObj["properties"]["sensorType"]))
            deviceSensor = device.getSensorByType(pType)
            if deviceSensor is not None:
                deviceSensor.lastValue = float(msgObj["properties"]["sensorValueFloat"])
    return True


async def receiver(ws, pObject: dSSConnectionData):
    while True:
        try:
            message = await ws.recv()
            onMessage(message, pObject)

        except websockets.exceptions.ConnectionClosed:
            print("ConnectionClosed")
        break


async def initWS(hass, pObject: dSSConnectionData):
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    async for websocket in websockets.connect(
        "wss://" + pObject.ipadress + ":8080/websocket?token=" + pObject.sessiontoken,
        ssl=ssl_ctx,
    ):
        try:
            while True:
                message = await websocket.recv()
                await onMessage(message, pObject)
        except websockets.ConnectionClosed:
            continue


async def fetchAppToken(pObject: dSSConnectionData) -> bool:
    try:
        pObj = await readdJsonFromUrlAsync(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/requestApplicationToken?applicationName=home_assistant_integration"
        )
        if "result" in pObj:
            if "applicationToken" in pObj["result"]:
                pObject.apptoken = pObj["result"]["applicationToken"]
                pObject.tokenState = TokenState.pending
                pObject.connectionState = ConnectionState.reachable
                return await enableAppToken(pObject)
        return True
    except:
        pObject.connectionState = ConnectionState.notReachable
    return False


async def enableAppToken(pObject: dSSConnectionData) -> bool:
    try:
        pObj = await readdJsonFromUrlAsync(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/login?user=dssadmin&password="
            + urllib.parse.quote(pObject.password)
        )
        if "result" in pObj:
            if "token" in pObj["result"]:
                pObject.sessiontoken = pObj["result"]["token"]
                pObject.passwordState = PasswordState.right
                return await enableAppTokenP2(pObject)
        return False
    except:
        pObject.passwordState = PasswordState.wrong
        return False


async def enableAppTokenP2(pObject: dSSConnectionData) -> bool:
    try:
        pObj = await readdJsonFromUrlAsync(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/enableToken?applicationToken="
            + pObject.apptoken
            + "&token="
            + pObject.sessiontoken
        )
        if "ok" in pObj:
            if pObj["ok"]:
                pObject.tokenState = TokenState.approved
                return True
    except:
        pObject.tokenState = TokenState.notWorking
    return False


def ensureSessionToken(pObject):
    if pObject.ipadress is None:
        return
    try:
        if pObject.sessiontoken is not None:
            sFinalURL = (
                "https://"
                + pObject.ipadress
                + ":8080/json/property/query2/?token="
                + pObject.sessiontoken
            )
            pObj = readdJsonFromUrl(sFinalURL)
            return
    except:
        pObject.sessiontoken = None
    try:
        if pObject.sessiontoken is None:
            pObject.tokenState = TokenState.notWorking
            pObj = readdJsonFromUrl(
                "https://"
                + pObject.ipadress
                + ":8080/json/system/loginApplication?loginToken="
                + pObject.apptoken
            )
            if "result" in pObj:
                if "token" in pObj["result"]:
                    pObject.sessiontoken = pObj["result"]["token"]
                    pObject.tokenState = TokenState.approved
    except Exception as error:
        print(error)
        pObject.tokenState = TokenState.notWorking
        return
    return


async def ensureSessionTokenAsync(pObject):
    if pObject.ipadress is None:
        return
    try:
        if pObject.sessiontoken is not None:
            sFinalURL = (
                "https://"
                + pObject.ipadress
                + ":8080/json/property/query2/?token="
                + pObject.sessiontoken
            )
            pObj = await readdJsonFromUrlAsync(sFinalURL)
            return
    except:
        pObject.sessiontoken = None
    try:
        if pObject.sessiontoken is None:
            pObject.tokenState = TokenState.notWorking
            pObj = await readdJsonFromUrlAsync(
                "https://"
                + pObject.ipadress
                + ":8080/json/system/loginApplication?loginToken="
                + pObject.apptoken
            )
            if "result" in pObj:
                if "token" in pObj["result"]:
                    pObject.sessiontoken = pObj["result"]["token"]
                    pObject.tokenState = TokenState.approved
    except Exception as error:
        print(error)
        pObject.tokenState = TokenState.notWorking
        return
    return


def readdJsonFromUrl(url) -> json:
    # A GET request to the API
    response = requests.get(url, verify=False, timeout=5000)

    # Print the response
    return response.json()


async def readdJsonFromUrlAsync(url) -> json:
    # A GET request to the API
    client = httpx.AsyncClient(verify=False)
    response = await client.get(url)
    # Print the response
    return response.json()


def ajaxSyncRequest(
    pObject: dSSConnectionData, url, param: dict[str, str], fRetry: bool
):
    try:
        ensureSessionToken(pObject)
        param["token"] = pObject.sessiontoken
        url = "https://" + pObject.ipadress + ":8080/json/" + url + "?"
        for sKey in param:
            url += sKey + "=" + str(param[sKey]) + "&"
        pObj = readdJsonFromUrl(url)
        if "ok" in pObj:
            if pObj["ok"] is False:
                if fRetry is False:
                    pObject.sessiontoken = None
                    return ajaxSyncRequest(pObject, url, param, True)
        if "result" in pObj:
            return pObj["result"]
    except:
        if fRetry is False:
            pObject.sessiontoken = None
            return ajaxSyncRequest(pObject, url, param, True)


def executeUDA(pObject: dSSConnectionData, udaID):
    try:
        ensureSessionToken(pObject)
        readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/event/raise?name=highlevelevent&parameter=id="
            + udaID
            + "&token="
            + pObject.sessiontoken
        )
    except:
        pObject.sessiontoken = None


def fetchStates(pObject: dSSConnectionData):
    try:
        ensureSessionToken(pObject)
    except:
        pObject.sessiontoken = None


def propertyQuery(pObject: dSSConnectionData, queryPath: str, fRetry: bool):
    try:
        ensureSessionToken(pObject)
        pObj = readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/property/query2?query="
            + queryPath
            + "&token="
            + pObject.sessiontoken
        )
        if "ok" in pObj:
            if pObj["ok"] is False:
                if fRetry is False:
                    pObject.sessiontoken = None
                    return propertyQuery(pObject, queryPath, True)
        if "result" in pObj:
            return pObj["result"]
    except:
        if fRetry is False:
            pObject.sessiontoken = None
            return propertyQuery(pObject, queryPath, True)


async def pollMetering(hass: HomeAssistant, pObject: dSSConnectionData):
    while True:
        try:
            pObjPower = await readdJsonFromUrlAsync(
                "https://"
                + pObject.ipadress
                + ":8080/json/metering/getLatest?from=.meters(all)&type=power&token="
                + pObject.sessiontoken
            )
            pObjEnergy = await readdJsonFromUrlAsync(
                "https://"
                + pObject.ipadress
                + ":8080/json/metering/getLatest?from=.meters(all)&type=energy&token="
                + pObject.sessiontoken
            )
            if "result" in pObjPower:
                if "values" in pObjPower["result"]:
                    for oData in pObjPower["result"]["values"]:
                        dsuid = oData["dSUID"]
                        circuit = pObject.getCircuitForId(dsuid)
                        if circuit is not None:
                            fDataIsNew = circuit.sensorW != float(oData["value"])
                            circuit.sensorW = float(oData["value"])
                            if fDataIsNew:
                                source = circuit.hassObjectW.entity_id
                                current_state = hass.states.get(source)
                                hass.states.async_set(
                                    source,
                                    current_state.state,
                                    current_state.attributes,
                                    force_update=True,
                                )
            if "result" in pObjEnergy:
                if "values" in pObjEnergy["result"]:
                    for oData in pObjEnergy["result"]["values"]:
                        dsuid = oData["dSUID"]
                        circuit = pObject.getCircuitForId(dsuid)
                        if circuit is not None:
                            fDataIsNew = circuit.sensorWH != float(oData["value"])
                            circuit.sensorWH = float(oData["value"])
                            if fDataIsNew:
                                source = circuit.hassObjectWH.entity_id
                                current_state = hass.states.get(source)
                                hass.states.async_set(
                                    source,
                                    current_state.state,
                                    current_state.attributes,
                                    force_update=True,
                                )
        except Exception as error:
            print("An exception occurred:", error)
            await ensureSessionTokenAsync(pObject)
        await sleep(1)
