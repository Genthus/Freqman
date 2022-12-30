from aqt import mw

configData = None

def getPreferences():
    assert mw.col, 'Tried to use preferences with no collection loaded'
    addonsConfig = mw.col.get_config('addons')
    if addonsConfig == None or 'morphboy' not in addonsConfig:
        # No config yet in the the collection.
        addMissingJsonConfig()
        prefs = getPreferences()
    else:
        prefs = addonsConfig['morphboy']
    return prefs

def getJsonConfig():
    global configData 
    if configData is None:
        configData = getPreferences()
    return configData

def defaultJson():
    'freqDictFilename' : 'jpdb.json'
    return {
        'filter':[
            { 'type': 'Basic', 'field': 'Expression'},
        ],
    }

def addMissingJsonConfig():
    # this ensures forward compatibility, because it adds new options in configuration (introduced by update) without
    # any notice with default value
    current = getJsonConfig().copy()
    default = defaultJson()
    for key, value in default.items():
        if key not in current:
            current[key] = value
    updatePreferences(current)

def updatePreferences(jcfg):
    curr_config = getJsonConfig()
    old_config = curr_config.copy()

    curr_config.update(jcfg)
    
    if not curr_config == old_config:
        addons_config = mw.col.get_config('addons')
        if addons_config is None:
            addons_config = {}
        addons_config['morphboy'] = curr_config.copy()
        mw.col.set_config('addons', addons_config)
