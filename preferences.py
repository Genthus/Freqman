from aqt import mw

prefData = None

def prefInit():
    global prefData
    prefData = None
    getPreferences()

def getPreferences():
    addonsConfig = mw.addonManager.getConfig('Freqman')
    addMissingJsonConfig()
    return addonsConfig

def getPrefs():
    global prefData 
    if prefData == None:
        prefData = getPreferences()
    return prefData

def defaultJson():
    return {
        "filter": [{ "field": "Expression", "type": "notBasic", "modify": False }],
        "setDict": "None",
        "dictStyle": "Rank",
        "tags": { "known": "fmKnown", "sorted": "fmSorted", "tracked": "fmTracked" },
        "general": {
            "onSync" : { "text": "Run with sync", "value": False },
            "ignoreSusLeech" : { "text": "Ignore suspened leeches", "value": False },
        }
    }

def addMissingJsonConfig():
    current = {}
    global prefData
    if prefData != None:
        current = getPrefs().copy()
    default = defaultJson()
    for key, value in default.items():
        if key not in current:
            current[key] = value
    mw.addonManager.writeConfig('Freqman',current)
    prefData = current

def updatePrefs(newCfg):
    current = getPrefs().copy()
    if current == None:
        getPreferences()
    for k, v in newCfg.items():
        current[k] = v
    mw.addonManager.writeConfig('Freqman',current)
    global prefData
    prefData = current

def resetPrefs():
    updatePrefs(defaultJson())
