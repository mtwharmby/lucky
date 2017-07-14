'''
Created on 6 Nov 2015

@author: wnm24546
'''
import sys
from PyQt4.QtGui import (QHBoxLayout, QWidget, QPushButton, QApplication, QDialog)
from CalibrationConfigView import CalibrationConfigView

class MainView(QWidget):

    def __init__(self):
        super(MainView, self).__init__(parent=None)
        
        btn = QPushButton("Push")
        btn.clicked.connect(self.btnClick)
        layout = QHBoxLayout()
        layout.addWidget(btn)
        self.setLayout(layout)
        
    def btnClick(self):
        self.bar = CalibrationConfigView(self)
        self.bar.exec_()



