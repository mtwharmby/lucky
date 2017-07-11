'''
Created on 6 Nov 2015

@author: wnm24546
'''

from PyQt4.QtGui import (QHBoxLayout, QWidget, QPushButton, QApplication, QDialog)

class CalibrationConfigView(QDialog):

    def __init__(self, parent_widget):
        super(CalibrationConfigView, self).__init__(parent=parent_widget)
        btn = QPushButton("Push")
        btn.clicked.connect(self.btnClick)
        layout = QHBoxLayout()
        layout.addWidget(btn)
        self.setLayout(layout)
    
    def btnClick(self):
        print "Yay!"