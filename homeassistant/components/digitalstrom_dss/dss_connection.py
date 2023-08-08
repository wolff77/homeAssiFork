import json
import urllib.parse

import requests

from .dss_data import UDA, ConnectionState, PasswordState, TokenState, dSSConnectionData


def fetchAppToken(pObject: dSSConnectionData) -> bool:
    try:
        pObj = readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/requestApplicationToken?applicationName=home_assistant_integration"
        )
        if "result" in pObj:
            if "applicationToken" in pObj["result"]:
                pObject.apptoken = pObj["result"]["applicationToken"]
                pObject.tokenState = TokenState.pending
                pObject.connectionState = ConnectionState.reachable
                enableAppToken(pObject)
        return True
    except:
        pObject.connectionState = ConnectionState.notReachable
    return False


def enableAppToken(pObject: dSSConnectionData) -> bool:
    try:
        pObj = readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/login?user=dssadmin&password="
            + urllib.parse.quote(pObject.password)
        )
        if "result" in pObj:
            if "token" in pObj["result"]:
                pObject.sessiontoken = pObj["result"]["token"]
                pObject.passwordState = PasswordState.right
                enableAppTokenP2(pObject)
        return True
    except:
        pObject.passwordState = PasswordState.wrong
        return False


def enableAppTokenP2(pObject: dSSConnectionData) -> bool:
    try:
        pObj = readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/system/enableToken?applicationToken="
            + pObject.apptoken
            + "&token="
            + pObject.sessiontoken
        )
        if "result" in pObj:
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
                    pObject.tokenUpdates += 1
    except:
        pObject.tokenState = TokenState.notWorking
        return
    return


def readdJsonFromUrl(url) -> json:
    # A GET request to the API
    response = requests.get(url, verify=False, timeout=5000)

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


def fetchUDA(pObject: dSSConnectionData, fRetry: bool) -> bool:
    try:
        ensureSessionToken(pObject)
        pObj = readdJsonFromUrl(
            "https://"
            + pObject.ipadress
            + ":8080/json/property/query2?query=/usr/events/*(*)&token="
            + pObject.sessiontoken
        )
        if "ok" in pObj:
            if pObj["ok"] is False:
                if fRetry is False:
                    pObject.sessiontoken = None
                    return fetchUDA(pObject, True)
        if "result" in pObj:
            pObject.UDAs = []
            for keys in pObj["result"]:
                newUDA = UDA(pObj["result"][keys]["id"], pObj["result"][keys]["name"])
                pObject.UDAs.append(newUDA)

    except:
        if fRetry is False:
            pObject.sessiontoken = None
            return fetchUDA(pObject, True)


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
