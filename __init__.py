from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from .preferences import getJsonConfig
from .ordering import orderCards

# startup
getJsonConfig()

# create a new menu item, "test"
reorder = QAction("Reorder Cards", mw)
prefMenu = QAction("Preferences", mw)
# set it to call testFunction when it's clicked
qconnect(reorder.triggered, orderCards)
# and add it to the tools menu
menuBar = mw.menuBar()
mbMenu = menuBar.addMenu('&Morphboy')
mbMenu.addAction(reorder)
mbMenu.addAction(prefMenu)

