from aqt import mw
import json
from datetime import datetime

prefData = None

def prefInit():
    global prefData
    prefData = None
    getPrefs()

def getPrefs() -> dict:
    global prefData 
    if prefData == None:
        prefData = mw.addonManager.getConfig('Freqman')
        prefData = addMissingJsonConfig(prefData)
    return prefData

def defaultJson():
    return {
        "filter": [
            { "field": "Field", "tags": [], "type": "notBasic", "modify": False }
        ],
        "setDict": "None",
        "lastSortedDict": "None",
        "dictStyle": "Rank",
        "lastUpdate": "",
        "tags": {
            "known": "fmKnown",
            "sorted": "fmSorted",
            "tracked": "fmTracked"
        },
        "general": {
            "afterSync": { "text": "Run reorder after sync", "value": False },
            "ignoreSusLeech": { "text": "Ignore suspened leeches", "value": True },
            "refresh": {
                "text": "Schedule refresh on next recalculation",
                "value": True
            }
        }
    }

def addMissingJsonConfig(d):
    pd = {}
    if d != None:
        pd = d.copy()
    for k,v in defaultJson().items():
        if k not in pd:
            pd[k] = v
        if type(k) == map:
            for k2,v2 in v.items():
                if k2 not in pd[k]:
                    pd[k][k2] = v2
    return pd

def getDaysSinceLastUpdate():
    last = getPrefs()['lastUpdate']
    if last == "":
        return 100000
    delta = datetime.now() - datetime.fromisoformat(last)
    return delta.days

def getGeneralOption(id):
    return getPrefs()['general'][id]['value']

def setGeneralOption(id,val):
    current = getPrefs().copy()
    try:
        current['general'][id]['value'] = val
    except KeyError:
        print("Key error setting general option with key: " + id)
    updatePrefs(current)

def setPref(id, val):
    current = getPrefs().copy()
    try:
        current[id] = val
    except KeyError:
        print("Key error setting pref with key: " + id)
    updatePrefs(current)

def updatePrefs(newCfg):
    current = getPrefs().copy()
    for k, v in newCfg.items():
        current[k] = v
    mw.addonManager.writeConfig('Freqman',current)
    global prefData
    prefData = current

def resetPrefs():
    updatePrefs(defaultJson())
