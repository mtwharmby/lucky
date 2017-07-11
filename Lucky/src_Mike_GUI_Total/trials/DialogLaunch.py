'''
Created on 6 Nov 2015

@author: wnm24546
'''
import sys
from PyQt4.QtGui import (QHBoxLayout, QWidget, QPushButton, QApplication, QDialog)
from MainView import MainView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainView()
    w.show()
    sys.exit(app.exec_())