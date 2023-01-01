import os 
from aqt import mw

configData = {}

def configInit():
    global configData
    configData = loadDefault()

def config(k):
    if k in configData.keys():
        return configData[k]
    print("Error getting config")
    return ""
    
def loadDefault():
    return {
        'dbPath': os.path.join(mw.pm.profileFolder(),'fmDB'),
        'dictDB': os.path.join(mw.pm.profileFolder(),'fmDB','dict.db'),
        'userDB': os.path.join(mw.pm.profileFolder(),'fmDB','user.db')
    }
