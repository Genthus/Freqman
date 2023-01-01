from aqt import mw
from aqt import gui_hooks
from aqt.utils import qconnect
from aqt.qt import *
from .preferences import prefInit
from .ordering import orderCards
from .window import openPrefs
from .db import dbInit, dbClose
from .config import configInit


reorder = QAction("Reorder Cards", mw)
prefMenu = QAction("Preferences", mw)

qconnect(reorder.triggered, orderCards)
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
