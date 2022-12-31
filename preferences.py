from aqt import mw
import json

configData = None

def getPreferences():
    addonsConfig = mw.addonManager.getConfig('Freqman')
    if addonsConfig == None or addonsConfig == {}:
        # No config yet in the the collection.
        addMissingJsonConfig()
        addonsConfig = mw.addonManager.getConfig('Freqman')
    return addonsConfig

def getConfig() -> dict:
    global configData 
    if configData == None:
        configData = getPreferences()
    return configData

def defaultJson():
    with open("config.json",'r') as f:
        return json.load(f)

def addMissingJsonConfig():
    current = getConfig().copy()
    default = defaultJson()
    for key, value in default.items():
        if key not in current:
            current[key] = value
    mw.addonManager.writeConfig('Freqman',current)

def updateConfig(newCfg):
    mw.addonManager.writeConfig('Freqman',newCfg)
    global configData
    configData = newCfg
