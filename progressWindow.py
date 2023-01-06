from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from aqt import mw
from aqt.qt import *
from .ordering import recalculate
from .db import dbClose

class Thread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(Thread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        # TODO make the progress bar reflect actual progress
        recalculate()
        dbClose()
        self._signal.emit(100)
        

class RecalcBox(QDialog):
    def __init__(self,parent=None):
        super(RecalcBox,self).__init__(parent)

        self.setModal(True)
        self.resize(300,100)

        self.setWindowTitle("Freqman")
        self.pbar = QProgressBar(self)
        self.pbar.setValue(10)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.pbar)
        self.setLayout(self.vbox)

        self.action()

    def action(self):
        # Close DBs to run in a new thread
        dbClose()

        self.thread = Thread()
        self.thread._signal.connect(self.signal_accept)
        self.thread.start()

    def signal_accept(self, msg):
        self.pbar.setValue(int(msg))
        if self.pbar.value() >= 99:
            self.close()
        

def openRecalc():
    mw.fmRecalc = RecalcBox(mw)
    mw.fmRecalc.show()
