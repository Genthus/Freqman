import os 
from aqt import mw

def config(k):
    if k in loadDefault().keys():
        return loadDefault()[k]
    print("Error getting config")
    return ""
    
def loadDefault():
    return {
        'dbPath': os.path.join(mw.pm.profileFolder(),'fmDB'),
        'dictDB': os.path.join(mw.pm.profileFolder(),'fmDB','dict.db'),
        'userDB': os.path.join(mw.pm.profileFolder(),'fmDB','user.db')
    }
