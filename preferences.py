from aqt import mw
import json
from datetime import datetime

prefData = None

addonName = 'Freqman'

def prefInit():
    changeAddonName()

    global prefData
    prefData = None
    getPrefs()

def changeAddonName():
    global addonName
    tempName = addonName
    for addonMeta in mw.addonManager.all_addon_meta():
        if addonMeta.human_name() == addonName:
            tempName = addonMeta.dir_name
        if addonMeta.dir_name == addonName:
            tempName = addonName
            break
    addonName = tempName

def getPrefs() -> dict:
    global prefData 
    if prefData == None:
        prefData = mw.addonManager.getConfig(addonName)
        updatePrefs(addMissingJsonConfig(prefData))
    return prefData

def defaultJson():
    return mw.addonManager.addonConfigDefaults(addonName)

def addMissingJsonConfig(d: dict):
    default = defaultJson()
    pd = {}
    if d != None:
        pd = d.copy()
    for k, v in pd.items():
        if type(v) == dict:
            for k2,v2 in v.items():
                default[k][k2] = v2
        else:
            default[k] = v
    return default

def newDictSelected():
    current = getPrefs()
    if current['setDict'] != current['lastSortedDict']:
        return True
    return False

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
    global prefData
    prefData = current
    mw.addonManager.writeConfig(addonName,current)
    if prefData != None:
        if current['filter'] != prefData['filter']:
            setGeneralOption('refresh', True)

def resetPrefs():
    updatePrefs(defaultJson())
