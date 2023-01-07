from aqt import mw
from aqt import gui_hooks
from aqt.utils import qconnect
from aqt.qt import *
from .preferences import prefInit
from .progressWindow import openRecalc, afterSyncReorder
from .window import openPrefs
from .db import dbInit


reorder = QAction("Reorder Cards", mw)
prefMenu = QAction("Preferences", mw)

qconnect(reorder.triggered, openRecalc)
qconnect(prefMenu.triggered, openPrefs)

menuBar = mw.menuBar()
mbMenu = menuBar.addMenu('&Freqman')
mbMenu.addAction(reorder)
mbMenu.addAction(prefMenu)

# startup
def addonInit():
    prefInit()

mw.addonManager.setConfigAction("Freqman", openPrefs)

gui_hooks.profile_did_open.append(addonInit)
gui_hooks.sync_did_finish.append(afterSyncReorder)

