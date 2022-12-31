from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from aqt import mw
from aqt.qt import *


class PrefWindow(QDialog):
    def __init__(self,parent=None):
        super(PrefWindow,self).__init__(parent)

        self.setModal(True)
        self.rowGui = []
        self.resize(500,500)

        self.setWindowTitle("Freqman Preferences")
        self.vbox = QVBoxLayout(self)
        self.tabWidget = QTabWidget()
        self.vbox.addWidget(self.tabWidget)

        self.createNoteFilterTab()
        self.createDictSelectTab()

    def createNoteFilterTab(self):
        self.frame1 = QWidget()
        self.tabWidget.addTab(self.frame1,"Note Filter")
        vbox = QVBoxLayout()
        self.frame1.setLayout(vbox)

    def createDictSelectTab(self):
        self.frame2 = QWidget()
        self.tabWidget.addTab(self.frame2,"Dictionary Selection")
        vbox = QVBoxLayout()
        self.frame2.setLayout(vbox)

def openPrefs():
    mw.fm =  PrefWindow(mw)
    mw.fm.show()
