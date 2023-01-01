from aqt import mw
import json

prefData = None

def prefInit():
    global prefData
    prefData = None
    getPreferences()

def getPreferences():
    addonsConfig = mw.addonManager.getConfig('Freqman')
    if addonsConfig == None or addonsConfig == {}:
        # No config yet in the the collection.
        addMissingJsonConfig()
        addonsConfig = mw.addonManager.getConfig('Freqman')
    return addonsConfig

def getPrefs() -> dict:
    global prefData 
    if prefData == None:
        prefData = getPreferences()
    return prefData

def defaultJson():
    with open("config.json",'r') as f:
        return json.load(f)

def addMissingJsonConfig():
    current = getPrefs().copy()
    default = defaultJson()
    for key, value in default.items():
        if key not in current:
            current[key] = value
    mw.addonManager.writeConfig('Freqman',current)

def updatePrefs(newCfg):
    mw.addonManager.writeConfig('Freqman',newCfg)
    global prefData
    prefData = newCfg
