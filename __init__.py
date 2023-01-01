from aqt import mw
from aqt import gui_hooks
from anki import hooks
from aqt.utils import qconnect
from aqt.qt import *
from .preferences import prefInit
from .ordering import recalculate
from .window import openPrefs
from .db import dbInit, dbClose, addCardToUpdate
from .config import configInit


reorder = QAction("Reorder Cards", mw)
prefMenu = QAction("Preferences", mw)

qconnect(reorder.triggered, recalculate)
qconnect(prefMenu.triggered, openPrefs)

menuBar = mw.menuBar()
mbMenu = menuBar.addMenu('&Freqman')
mbMenu.addAction(reorder)
mbMenu.addAction(prefMenu)

# startup
def addonInit():
    configInit()
    prefInit()
    dbInit()

gui_hooks.profile_did_open.append(addonInit)
gui_hooks.profile_will_close.append(dbClose)
hooks.card_will_flush.append(addCardToUpdate)
mw.addonManager.setConfigAction("Freqman", openPrefs)

