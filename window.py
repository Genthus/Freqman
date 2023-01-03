from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from aqt import mw
from aqt.qt import *
from .preferences import getPrefs, updatePrefs, resetPrefs
from .db import importYomichanFreqDict, getDicts, rmDictFromDB
from .ordering import cleanUserData

class PrefWindow(QDialog):
    def __init__(self,parent=None):
        super(PrefWindow,self).__init__(parent)

        self.setModal(True)
        self.resize(700,400)

        self.rowGui = []
        self.dictPath = QLineEdit("Not selected")

        self.setWindowTitle("Freqman Preferences")
        self.vbox = QVBoxLayout(self)
        self.tabWidget = QTabWidget()
        self.vbox.addWidget(self.tabWidget)

        self.createGeneralSettingsTab()
        self.createNoteFilterTab()
        self.createDictSelectTab()
        self.createButtons()

        self.setLayout(self.vbox)

    def createGeneralSettingsTab(self):
        self.frame1 = QWidget()
        self.tabWidget.addTab(self.frame1,"General")
        vbox = QVBoxLayout()
        self.frame1.setLayout(vbox)
        vbox.setContentsMargins(10,20,10,10)

        topLayout = QFormLayout() 
        self.genSettings = {}
        settings = getPrefs()['general']
        for k,v in settings.items():
            gen = QCheckBox()
            gen.setChecked(v['value'])
            self.genSettings[k] = (v['text'], gen)
            topLayout.addRow(v['text'],gen)

        vbox.addLayout(topLayout)

        resetButton = QPushButton("&Reset Preferences")
        vbox.addWidget(resetButton, 1, Qt.AlignRight)
        resetButton.setMaximumWidth(150)
        resetButton.clicked.connect(self.reset)

        resetDBButton = QPushButton("&Reset database and tags")
        vbox.addWidget(resetDBButton, 1, Qt.AlignRight)
        resetDBButton.setMaximumWidth(150)
        resetDBButton.clicked.connect(self.resetDB)

    def reset(self):
        resetPrefs()
        self.tabWidget.clear()
        self.createGeneralSettingsTab()
        self.createNoteFilterTab()
        self.createDictSelectTab()

    def resetDB(self):
        cleanUserData()

    def createNoteFilterTab(self):
        self.frame2 = QWidget()
        self.tabWidget.addTab(self.frame2,"Note Filter")
        vbox = QVBoxLayout()
        self.frame2.setLayout(vbox)
        vbox.setContentsMargins(10,20,10,10)

        self.tableModel = QStandardItemModel(0, 3)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableModel.setHeaderData(0,Qt.Horizontal, "Note Type")
        self.tableModel.setHeaderData(1,Qt.Horizontal, "Field")
        self.tableModel.setHeaderData(2,Qt.Horizontal, "Modify")

        rowData = getPrefs()['filter']
        self.tableModel.setRowCount(len(rowData))
        self.rowGui = []
        for i,row in enumerate(rowData):
            self.setTableRow(i,row)

        label = QLabel(
            "Select the card types you want to include."
            +"\nField determines which part of the card will be looked for."
            +"\nIf Modify is off, the cards will not have their order modified."
        )
        label.setWordWrap(True)
        vbox.addWidget(label)
        vbox.addSpacing(20)
        vbox.addWidget(self.tableView)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.clone = self.mkBtn("Clone", self.onClone, hbox)
        self.delete = self.mkBtn("Delete", self.onDelete, hbox)

    def createDictSelectTab(self):
        self.frame3 = QWidget()
        self.tabWidget.addTab(self.frame3,"Dictionary Selection")
        vbox = QVBoxLayout()
        self.frame3.setLayout(vbox)
        vbox.setContentsMargins(10,20,10,10)

        topLayout = QFormLayout()
        self.dictComboBox = QComboBox()
        self.getDictComboBox()
        topLayout.addRow("Current Dictionary:",self.dictComboBox)
        dictStyle = QComboBox()
        dictStyle.addItem("Rank")
        dictStyle.addItem("Occurrence")
        if getPrefs()['dictStyle'] != "Rank":
            dictStyle.setCurrentIndex(1)
        self.dictStyle = dictStyle
        topLayout.addRow("Sorting mode:",self.dictStyle)
        buttonDeleteDict = QPushButton("&Remove Dictionary")
        buttonDeleteDict.setMaximumWidth(150)
        buttonDeleteDict.clicked.connect(self.rmDict)
        topLayout.addRow("",buttonDeleteDict)
        vbox.addLayout(topLayout)
        
        bottomLayout = QVBoxLayout()
        newDictLabel = QLabel("Import new dictionary")
        bottomLayout.addWidget(newDictLabel)

        hbox = QHBoxLayout()
        buttonSearchDict = QPushButton("&Select")
        buttonSearchDict.setMaximumWidth(150)
        buttonSearchDict.clicked.connect(self.getFile)
        hbox.addWidget(buttonSearchDict)
        hbox.addWidget(self.dictPath)
        bottomLayout.addLayout(hbox)

        buttonImportDict = QPushButton("&Import")
        buttonImportDict.setMaximumWidth(150)
        buttonImportDict.clicked.connect(self.importDict)
        bottomLayout.addWidget(buttonImportDict)
        vbox.addLayout(bottomLayout)

    def rmDict(self):
        reply = QMessageBox.question(self,'Remove Dictionary','Are you sure you?',QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if reply == QMessageBox.Yes:
            rmDictFromDB(self.dictComboBox.currentText())
            self.getDictComboBox()

    def getDictComboBox(self):
        assert self.dictComboBox
        self.dictComboBox.clear()
        self.dictComboBox.addItem("None")
        active = 0
        for i,dict in enumerate(getDicts()):
            if dict[0] == getPrefs()['setDict']:
                active = i + 1
            self.dictComboBox.addItem(dict[0])
        self.dictComboBox.setCurrentIndex(active)

    def getFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '~',"Zip files (*.zip)")
        self.dictPath.setText(fname[0])

    def importDict(self):
        if self.dictPath.text() != "Not selected":
            res = importYomichanFreqDict(self.dictPath.text())
            if "Success" not in res:
                err = QMessageBox(self)
                err.setText("Error: " + res)
                err.exec()
            err = QMessageBox(self)
            err.setText(res)
            err.exec()
            self.getDictComboBox()
        else:
            err = QMessageBox(self)
            err.setText("No file selected")
            err.exec()

    def createButtons(self):
        hbox = QHBoxLayout()
        self.vbox.addLayout(hbox)
        buttonCancel = QPushButton("&Cancel")
        hbox.addWidget(buttonCancel, 1, Qt.AlignRight)
        buttonCancel.setMaximumWidth(150)
        buttonCancel.clicked.connect(self.onCancel)

        buttonOkay = QPushButton("&Apply")
        hbox.addWidget(buttonOkay)
        buttonOkay.setMaximumWidth(150)
        buttonOkay.clicked.connect(self.onOkay)

    def onCancel(self):
        self.close()

    def readConfigFromGui(self):
        cfg = {}
        cfg['filter'] = []
        for _, rowGui in enumerate(self.rowGui):
            cfg['filter'].append(self.rowGuiToFilter(rowGui))
        cfg['setDict'] = self.dictComboBox.currentText()
        cfg['dictStyle'] = self.dictStyle.currentText()
        cfg['general'] = {}
        for k,v in self.genSettings.items():
            cfg['general'][k] = {'text' : v[0], 'value' : v[1].isChecked()}
        return cfg

    def rowGuiToFilter(self, row_gui):
        filter = {}

        filter['type'] = row_gui['modelComboBox'].currentText()
        filter['field'] = row_gui['fieldEntry'].text()
        filter['modify'] = row_gui['modifyCheckBox'].checkState() != Qt.Unchecked

        return filter

    def onOkay(self):
        updatePrefs(self.readConfigFromGui())
        self.close()

    def getCurrentRow(self):
        indexes = self.tableView.selectedIndexes()
        return 0 if len(indexes) == 0 else indexes[0].row()

    def appendRowData(self, data):
        self.tableModel.setRowCount(len(self.rowGui) + 1)
        self.setTableRow(len(self.rowGui), data)

    def rowIndexToFilter(self, rowIdx):
        return self.rowGuiToFilter(self.rowGui[rowIdx])

    def onDelete(self):
        # do not allow to delete the last row
        if len(self.rowGui) == 1:
            return
        row_to_delete = self.getCurrentRow()
        self.tableModel.removeRow(row_to_delete)
        self.rowGui.pop(row_to_delete)

    def onClone(self):
        row = self.getCurrentRow()
        data = self.rowIndexToFilter(row)
        self.appendRowData(data)

    def setTableRow(self, rowIndex, data):
        assert rowIndex >= 0, "Bruh, negative numbs setting rows"
        assert len(
            self.rowGui) >= rowIndex, "Row can't be appended because it would leave an empty row"

        rowGui = {}

        modelComboBox = QComboBox()
        active = 0
        for i, model in enumerate(mw.col.models.all_names_and_ids()):
            if model.name == data['type']:
                active = i 
            modelComboBox.addItem(model.name)
        modelComboBox.setCurrentIndex(active)

        modifyItem = QStandardItem()
        modifyItem.setCheckable(True)
        modifyItem.setCheckState(Qt.Checked if data.get('modify', True) else Qt.Unchecked)

        rowGui['modelComboBox'] = modelComboBox
        rowGui['fieldEntry'] = QLineEdit(data['field'])
        rowGui['modifyCheckBox'] = modifyItem

        def setColumn(col, widget):
            self.tableView.setIndexWidget(self.tableModel.index(rowIndex, col), widget)

        setColumn(0, rowGui['modelComboBox'])
        setColumn(1, rowGui['fieldEntry'])
        self.tableModel.setItem(rowIndex, 2, modifyItem)

        if len(self.rowGui) == rowIndex:
            self.rowGui.append(rowGui)
        else:
            self.rowGui[rowIndex] = rowGui

    def mkBtn(self, txt, f, parent):
        b = QPushButton(txt)
        b.clicked.connect(f)
        parent.addWidget(b)

def openPrefs():
    mw.fm =  PrefWindow(mw)
    mw.fm.show()
