from aqt import mw
import json

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
    return mw.addonManager.addonConfigDefaults('Freqman')

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

def getGeneralOption(id):
    try:
        getPrefs()['general'][id]['value']
    except KeyError:
        print("Key error getting general option with key: " + id)

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
