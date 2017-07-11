#!/usr/bin/env python
 
from sip import setapi
setapi("QDate", 2)
setapi("QDateTime", 2)
setapi("QTextStream", 2)
setapi("QTime", 2)
setapi("QVariant", 2)
setapi("QString", 2)
setapi("QUrl", 2)
 
from PyQt4.QtCore import QObject
from PyQt4.QtGui import (QApplication, QDialog, QHBoxLayout,
                         QLabel, QListWidget, QPushButton,
                         QVBoxLayout,QDialogButtonBox)
import sys
 
 
def main():
    app = QApplication(sys.argv)
    view = ChainComposerDialog()
    composed = ChainComposer(view)
    composed.initialize()
    view.show()
    sys.exit(app.exec_())
 
 
class ChainComposer(QObject):
    def __init__(self, view, parent=None):
        super(ChainComposer, self).__init__(parent)
        self .__view = view
        view.setComposer(self)
 
    def initialize(self):
        self.__view.setSelectionList = ('Reverb',)
 
    def add(self, row):
        self.__view.addToChain(self.__view.filterAt(row))
 
 
class ChainComposerDialog(QDialog):
 
    def __init__(self, parent=None):
        super(ChainComposerDialog, self).__init__(parent)
        self.setWindowTitle('Composer Chain')
 
        layout = QVBoxLayout()
 
        mainLayout = QHBoxLayout()
 
        selectionLayout = QVBoxLayout()
        label = QLabel('Available Filters:')
        selectionLayout.addWidget(label)
        self.__selectionList = QListWidget()
        selectionLayout.addWidget(self.__selectionList)
        mainLayout.addLayout(selectionLayout)
 
        actionsLayout = QVBoxLayout()
        actionsLayout.addStretch()
        addButton = QPushButton('Add>>')
        addButton.clicked.connect(self.__handleAdd)
        actionsLayout.addWidget(addButton)
        removeButton = QPushButton('Remove')
        actionsLayout.addWidget(removeButton)
        removeAllButton = QPushButton('Remove All')
        actionsLayout.addWidget(removeAllButton)
        actionsLayout.addStretch()
        mainLayout.addLayout(actionsLayout)
 
        chainLayout = QVBoxLayout()
        chainLayout.addWidget(QLabel('Chain:'))
        self.__chainList = QListWidget()
        chainLayout.addWidget(self.__chainList)
        mainLayout.addLayout(chainLayout)
 
        layout.addLayout(mainLayout)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.okClick)
        buttonBox.rejected.connect(self.cancelClick)
        layout.addWidget(buttonBox)
 
#         buttonLayout = QHBoxLayout()
#         okButton = QPushButton('OK')
#         okButton.clicked.connect(self.accept)
#         buttonLayout.addWidget(okButton)
#         cancelButton = QPushButton('Cancel')
#         cancelButton.clicked.connect(self.reject)
#         buttonLayout.addWidget(cancelButton)
#         layout.addLayout(buttonLayout)
 
        self.setLayout(layout)
 
        self.__composer = None
    
    def okClick(self):
        print "OK!"
        self.accept()
    
    def cancelClick(self):
        print "Cancel"
        self.reject()
 
    def setComposer(self, composer):
        self.__composer = composer
 
    @property
    def selectionList(self):
        return self.__getStrings(self.__selectionList)
 
    @selectionList.setter
    def setSelectionList(self, filters):
        for i in xrange(self.__selectionList.count()):
            self.__selectionList.takeItem(i)
        self.__selectionList.addItems(filters)
 
    def filterAt(self, row):
        return self.__selectionList.item(row).text()
 
    def addToChain(self, filterName):
        self.__chainList.addItem(filterName)
 
    @property
    def composedFilter(self):
        return self.__getStrings(self.__chainList)
 
    @staticmethod
    def __getStrings(listWidget):
        return tuple(listWidget.item(i) for i in
                     range(listWidget.count()))
 
    def __handleAdd(self):
        if self.__composer is None:
            return
        for item in self.__selectionList.selectedItems():
            row = self.__selectionList.row(item)
            self.__composer.add(row)
 
 
if __name__ == '__main__':
    main()