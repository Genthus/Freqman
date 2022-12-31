from aqt import mw
from os.path import exists

configData = None

def getPreferences():
    addonsConfig = mw.addonManager.getConfig('morphboy')
    if addonsConfig == None or addonsConfig == {}:
        # No config yet in the the collection.
        addMissingJsonConfig()
    return addonsConfig

def getJsonConfig():
    global configData 
    if configData == None:
        configData = getPreferences()
    return configData

def defaultJson():
    return {
        'setDict' : '',
        'tags': {
            'known': 'mbKnown',
            'ranked': 'mbRanked'
        },
        'filter':[
            { 'type': 'notBasic', 'field': 'Expression'},
        ],
    }

def addMissingJsonConfig():
    if not exists("config.json"):
        with open("config.json",'w') as f:
            f.write("{}")
        mw.addonManager.writeConfig('morphboy',defaultJson())
        return
    current = getJsonConfig().copy()
    default = defaultJson()
    for key, value in default.items():
        if key not in current:
            current[key] = value
    mw.addonManager.writeConfig('morphboy',current)
