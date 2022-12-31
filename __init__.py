from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from .preferences import getJsonConfig
from .ordering import orderCards
from .window import openPrefs

# startup
getJsonConfig()

# create a new menu item, "test"
reorder = QAction("Reorder Cards", mw)
prefMenu = QAction("Preferences", mw)
# set it to call testFunction when it's clicked
qconnect(reorder.triggered, orderCards)
qconnect(prefMenu.triggered, openPrefs)
# and add it to the tools menu
menuBar = mw.menuBar()
mbMenu = menuBar.addMenu('&Morphboy')
mbMenu.addAction(reorder)
mbMenu.addAction(prefMenu)

